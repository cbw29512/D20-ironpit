(() => {
  "use strict";
  // Presentation only. Every fight is resolved by the existing combat engine;
  // this module renders sampled live battles without changing fight outcomes.
  const $ = id => document.getElementById(id);

  function find(rows, id, edition, side) {
    try {
      const card = (rows || []).find(item => item.runnable_template_id === id &&
        item.ruleset === edition && item.coverage_status === "raw_ready");
      if (!card) throw new Error(`Missing ${edition} ${side} card ${id} on battlefield.`);
      return card;
    } catch (error) {
      console.error("Bulk fight card projection failed", {id, edition, side, error});
      throw error;
    }
  }

  async function show(api, entry, battle, label) {
    try {
      const edition = entry.edition || entry.selection?.ruleset;
      if (api.state.ruleset !== edition) await api.ensureRuleset(edition, true);
      const {heroes, monsters} = api.state.catalog;
      let front, back;
      if (entry.kind === "punching_bag") {
        const bag = window.IRON_PIT_BATTLEFIELD_BAG_RUNNER?.bagCard(edition);
        if (!bag) throw new Error("Compiled homebrew Punching Bag is missing.");
        if (entry.source_kind === "pregen") {
          front = [find(heroes, entry.source_id, edition, "pregen")];
          back = [bag];
        } else {
          front = [bag];
          back = [find(monsters, entry.source_id, edition, "monster")];
        }
      } else {
        front = entry.selection.hero_ids.map(id => find(heroes, id, edition, "pregen"));
        back = entry.selection.monster_ids.map(id => find(monsters, id, edition, "monster"));
      }
      api.load(front, back, label);
      const slotMap = {heroes: front.map((_, i) => i), monsters: back.map((_, i) => i)};
      await window.IRON_PIT_BATTLEFIELD_REPLAY.play(battle, slotMap, {instant: true});
      window.IRON_PIT_BATTLEFIELD_VIEW.writeLog(battle);
      window.IRON_PIT_BATTLEFIELD_VIEW.showResult(battle);
      api.state.hasRun = true;
    } catch (error) {
      console.error("Could not display current bulk fight", {label, error});
      throw error;
    }
  }

  function progress(report, label) {
    try {
      const bar = $("bulk-progress");
      bar.max = report.total;
      bar.value = report.completed;
      $("bulk-status").textContent = `${label}: ${report.completed.toLocaleString()} / ` +
        `${report.total.toLocaleString()} · ${report.passed.toLocaleString()} passed · ` +
        `${report.failed.toLocaleString()} failed` +
        (report.stopped ? " · stopped" : "");
    } catch (error) {
      console.error("Could not update bulk combat progress", error);
      throw error;
    }
  }

  function visibleTranscript() {
    try {
      const battle = window.IRON_PIT_BULK_COMBAT_UI.lastBattle;
      if (!battle?.events?.length) throw new Error("Run a fight before exporting its log.");
      const readable = window.IRON_PIT_BATTLE_LOG_EXPORT.textFromBattle(battle);
      return "IRON PIT — COMPLETE VISIBLE FIGHT\n" +
        "Outcome: " + battle.outcome + " | Rounds: " + battle.rounds +
        " | Events: " + battle.events.length + "\n" +
        readable + "\n\nFULL RAW EVENTS (EVERY FIELD)\n" +
        JSON.stringify(battle.events, null, 2) + "\n";
    } catch (error) {
      console.error("Visible fight log formatting failed", error);
      throw error;
    }
  }

  async function copyVisible() {
    try {
      await navigator.clipboard.writeText(visibleTranscript());
      $("bulk-status").textContent = "Complete visible fight log copied.";
    } catch (error) {
      console.error("Copy combat log failed", error);
      $("bulk-status").textContent = "Could not copy combat log: " + error.message;
    }
  }

  function saveVisible() {
    try {
      const blob = new Blob([visibleTranscript()], {type: "text/plain;charset=utf-8"});
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "iron-pit-full-visible-fight-" + Date.now() + ".txt";
      document.body.append(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 5000);
    } catch (error) {
      console.error("Visible fight log download failed", error);
      $("bulk-status").textContent = "Download failed: " + error.message;
    }
  }

  function install(start, stop) {
    try {
      for (const id of ["bulk-bag", "bulk-pairs", "bulk-stop", "bulk-copy",
        "bulk-progress", "bulk-status", "bulk-save"]) {
        if (!$(id)) throw new Error("Missing simplified hero control " + id);
      }
      $("bulk-bag").addEventListener("click", () => { void start("bag"); });
      $("bulk-pairs").addEventListener("click", () => { void start("pairs"); });
      $("bulk-stop").addEventListener("click", stop);
      $("bulk-copy").addEventListener("click", () => { void copyVisible(); });
      $("bulk-save").addEventListener("click", saveVisible);
    } catch (error) {
      console.error("Simplified bulk control installation failed", error);
      throw error;
    }
  }

  window.IRON_PIT_BULK_COMBAT_UI = {install, show, progress, lastBattle: null};
})();