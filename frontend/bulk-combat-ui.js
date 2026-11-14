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

  async function copyVisible() {
    try {
      const battle = window.IRON_PIT_BULK_COMBAT_UI.lastBattle;
      if (!battle) throw new Error("Run a battle before copying its log.");
      const text = window.IRON_PIT_BATTLE_LOG_EXPORT.textFromBattle(battle);
      await navigator.clipboard.writeText(text);
      $("bulk-status").textContent = "Complete visible fight log copied.";
    } catch (error) {
      console.error("Copy combat log failed", error);
      $("bulk-status").textContent = "Could not copy combat log: " + error.message;
    }
  }

  function install(start, stop) {
    try {
      for (const id of ["bulk-bag", "bulk-pairs", "bulk-stop", "bulk-copy",
        "bulk-progress", "bulk-status"]) {
        if (!$(id)) throw new Error("Missing simplified hero control " + id);
      }
      $("bulk-bag").addEventListener("click", () => { void start("bag"); });
      $("bulk-pairs").addEventListener("click", () => { void start("pairs"); });
      $("bulk-stop").addEventListener("click", stop);
      $("bulk-copy").addEventListener("click", () => { void copyVisible(); });
    } catch (error) {
      console.error("Simplified bulk control installation failed", error);
      throw error;
    }
  }

  window.IRON_PIT_BULK_COMBAT_UI = {install, show, progress, lastBattle: null};
})();