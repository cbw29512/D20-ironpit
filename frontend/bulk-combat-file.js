(() => {
  "use strict";
  // State schema: one private OPFS transcript filename and one worker per suite.
  // The worker writes each fight to disk; no full-test array stays in memory.
  const KEY = "iron-pit-last-full-bulk-log";
  let recent = null;
  function latestName() {
    try { return recent || localStorage.getItem(KEY) || null; }
    catch (error) { console.warn("Could not restore saved bulk-log pointer", error); return recent; }
  }
  function remember(name) {
    recent = name;
    try { localStorage.setItem(KEY, name); }
    catch (error) { console.warn("Bulk log recovery pointer unavailable", error); }
  }
  function connect() {
    if (typeof Worker !== "function" || !navigator.storage?.getDirectory)
      throw new Error("Local combat logging requires a current Chrome or Edge browser.");
    const worker = new Worker("bulk-combat-log-worker.js");
    const pending = new Map();
    let serial = 0;
    worker.onmessage = ({data}) => {
      const request = pending.get(data?.id);
      if (!request) return;
      pending.delete(data.id);
      if (data.ok) request.resolve(data);
      else request.reject(new Error(data.error || "Local combat log write failed."));
    };
    worker.onerror = error => {
      console.error("Local combat logging worker crashed", error);
      for (const request of pending.values())
        request.reject(new Error("Local combat log worker crashed."));
      pending.clear();
    };
    const ask = (action, data = {}) => new Promise((resolve, reject) => {
      const id = ++serial;
      pending.set(id, {resolve, reject});
      try { worker.postMessage({id, action, ...data}); }
      catch (error) { pending.delete(id); reject(error); }
    });
    const terminate = () => {
      for (const request of pending.values())
        request.reject(new Error("Local combat log worker terminated."));
      pending.clear();
      worker.terminate();
    };
    return {ask, terminate};
  }
  async function open(mode, seed) {
    const name = "iron-pit-" + mode + "-complete-" + seed + "-" + Date.now() + ".txt";
    let link = null;
    try {
      link = connect();
      await link.ask("start", {name});
      const append = text => link.ask("append", {text});
      await append("IRON PIT — COMPLETE COMBAT TEST TRANSCRIPT\n" +
        "Mode: " + mode + " | Base seed: " + seed + "\n" +
        "Every engine event is retained, including the complete raw fields.\n" +
        "Unobserved abilities are NOT certified.\n\n");
      remember(name);
      let closed = false, fights = 0;
      const write = text => {
        if (closed) throw new Error("Local combat transcript already finalized.");
        return append(text);
      };
      return {
        name,
        async fight(index, total, entry, seedValue, battle, diagnostic, evidence = null) {
          try {
            if (!Array.isArray(battle?.events) || !battle.events.length)
              throw new Error("Engine returned no combat events.");
            const formatter = window.IRON_PIT_BATTLE_LOG_EXPORT?.textFromBattle;
            if (typeof formatter !== "function")
              throw new Error("Canonical combat transcript formatter is missing.");
            const title = entry.label || entry.card_name || entry.source_id;
            const heading = "\n========== FIGHT " + (index + 1) + " OF " + total +
              " ==========\nMATCHUP: " + title + " | EDITION: " +
              (entry.edition || entry.selection?.ruleset) +
              "\nSEED: " + seedValue + " | DIAGNOSTIC: " + (diagnostic || "not supplied") +
              "\nOUTCOME: " + battle.outcome + " | ROUNDS: " + battle.rounds +
              " | EVENTS: " + battle.events.length + "\n\n";
            const observed = evidence ? "\n===== SOURCE ABILITY EVIDENCE =====\n" +
              JSON.stringify(evidence, null, 2) + "\n" : "";
            const raw = battle.events.map((event, i) =>
              "EVENT " + (i + 1) + " RAW: " + JSON.stringify(event)).join("\n");
            await write(heading + formatter(battle) + observed + "\n\n" + raw +
              "\n========== END FIGHT ==========\n");
            fights++;
          } catch (error) {
            console.error("Could not retain complete fight transcript", {index, seedValue, error});
            throw error;
          }
        },
        async error(index, total, entry, seedValue, error) {
          try {
            await write("\n========== FIGHT " + (index + 1) + " OF " + total +
              ": ENGINE OR VALIDATION FAILURE ==========\nMATCHUP: " +
              (entry.label || entry.source_id) + " | SEED: " + seedValue +
              "\nERROR: " + (error?.stack || error?.message || String(error)) + "\n");
          } catch (writeError) {
            console.error("Combat failure could not be written to local log", writeError);
            throw writeError;
          }
        },
        async close(report) {
          if (closed) return;
          let failure = null;
          try {
            await write("\n========== SUMMARY ==========\n" +
              JSON.stringify({...report, fights_logged: fights}, null, 2) + "\n");
          } catch (error) { failure = error; }
          try { await link.ask("finish"); }
          catch (error) { failure ||= error; }
          closed = true;
          link.terminate();
          if (failure) throw failure;
        },
      };
    } catch (error) {
      link?.terminate();
      console.error("Could not start automatic local combat logging", {mode, seed, error});
      throw error;
    }
  }
  window.IRON_PIT_BULK_COMBAT_FILE = {open, latestName};
})();