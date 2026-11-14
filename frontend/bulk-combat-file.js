(() => {
  "use strict";
  // Full-log schema: one UTF-8 text file, every attempted fight, all engine
  // events (readable presentation AND unchanged raw JSON), and final totals.
  // Only a single fight is ever assembled in memory; no event sampling.
  async function open(mode, seed) {
    try {
      if (typeof window.showSaveFilePicker !== "function")
        throw new Error("Full streaming logs require Chrome or Edge with file saving enabled.");
      const file = await window.showSaveFilePicker({
        suggestedName: `iron-pit-${mode}-complete-${seed}.txt`,
        types: [{description: "Complete combat transcript", accept: {"text/plain": [".txt"]}}],
      });
      const writable = await file.createWritable();
      let closed = false, fights = 0;
      async function write(text) {
        if (closed) throw new Error("Combat transcript file is already closed.");
        await writable.write(text);
      }
      await write(`IRON PIT — COMPLETE COMBAT TEST TRANSCRIPT\n` +
        `Mode: ${mode} | Base seed: ${seed}\n` +
        "Every engine event is written below, including full raw event fields.\n" +
        "A pass is an observed result, not proof that all source abilities fired.\n\n");
      return {
        async fight(index, total, entry, seedValue, battle, diagnostic, evidence = null) {
          try {
            if (!Array.isArray(battle?.events) || !battle.events.length)
              throw new Error("Engine returned no combat events.");
            const formatter = window.IRON_PIT_BATTLE_LOG_EXPORT?.textFromBattle;
            if (typeof formatter !== "function")
              throw new Error("Canonical combat transcript formatter is missing.");
            const title = entry.label || entry.card_name || entry.source_id;
            const header = `\n========== FIGHT ${index + 1} OF ${total} ==========\n` +
              `MATCHUP: ${title} | EDITION: ${entry.edition || entry.selection?.ruleset}\n` +
              `SEED: ${seedValue} | DIAGNOSTIC: ${diagnostic || "not supplied"}\n` +
              `OUTCOME: ${battle.outcome} | ROUNDS: ${battle.rounds} | EVENTS: ${battle.events.length}\n\n`;
            // Narrative retains every event and its rule-audit lines.
            // Raw JSON retains every extra engine field the formatter may not display.
            const narrative = formatter(battle);
            const coverageText = evidence
              ? "\n===== OBSERVED AND UNOBSERVED SOURCE ABILITIES =====\n" +
                JSON.stringify(evidence, null, 2) + "\n"
              : "";
            const raw = battle.events.map((event, offset) =>
              `EVENT ${offset + 1} RAW: ${JSON.stringify(event)}`).join("\n");
            await write(header + narrative + coverageText + "\n\n" + raw +
              "\n========== END FIGHT ==========\n");
            fights++;
          } catch (error) {
            console.error("Full combat transcript write failed", {index, seedValue, error});
            throw error;
          }
        },
        async error(index, total, entry, seedValue, error) {
          try {
            await write(`\n========== FIGHT ${index + 1} OF ${total}: ENGINE FAILURE ==========\n` +
              `MATCHUP: ${entry.label || entry.source_id} | SEED: ${seedValue}\n` +
              `ERROR: ${error?.stack || error?.message || String(error)}\n` +
              "No combat events were returned; none have been fabricated.\n");
          } catch (writeError) {
            console.error("Engine failure could not be preserved in full log", writeError);
            throw writeError;
          }
        },
        async close(report) {
          if (closed) return;
          try {
            await write("\n========== SUMMARY ==========\n" +
              JSON.stringify({...report, fights_logged: fights}, null, 2) + "\n");
          } finally {
            closed = true;
            await writable.close();
          }
        },
      };
    } catch (error) {
      console.error("Could not open complete combat transcript file", {mode, seed, error});
      throw error;
    }
  }
  window.IRON_PIT_BULK_COMBAT_FILE = {open};
})();