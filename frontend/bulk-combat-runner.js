(() => {
  "use strict";
  // State: {running, stopRequested}; only one bulk suite can own the
  const BASE_SEED = 12345;
  const BAG_ATTEMPTS = 3;
  const $ = id => document.getElementById(id);
  let control = null;
  function inspect(battle, originals) {
    try {
      const problems = [];
      if (!Array.isArray(battle?.events) || !battle.events.length)
        problems.push("no_combat_events");
      if (!["heroes_win", "monsters_win", "draw"].includes(battle?.outcome))
        problems.push("invalid_outcome");
      if (battle.events?.some(event => event.event_type === "movement"))
        problems.push("forbidden_tactical_movement");
      for (const [card, serialized] of originals)
        if (JSON.stringify(card) !== serialized) problems.push("source_card_mutation");
      return problems;
    } catch (error) {
      console.error("Bulk combat evidence validation failed", error);
      throw error;
    }
  }
  function caseAt(plan, mode, index) {
    try {
      return mode === "bag" ? plan.at(Math.floor(index / BAG_ATTEMPTS)) : plan.at(index);
    } catch (error) {
      console.error("Bulk suite matchup lookup failed", {mode, index, error});
      throw error;
    }
  }
  async function execute(api, plan, mode, writer, report, flag) {
    const turbo = window.IRON_PIT_BROWSER_TURBO;
    const source = window.IRON_PIT_TEST_ALL_RUNNER?.sources;
    if (!turbo?.deriveSeed || !turbo?.runSeeded || !source)
      throw new Error("Canonical seeded combat and source resolver are unavailable.");
    for (let index = 0; index < report.total; index++) {
      if (flag.stopRequested) { report.stopped = true; break; }
      const entry = caseAt(plan, mode, index);
      const seed = entry.kind === "preset" ? entry.seed :
        turbo.deriveSeed(BASE_SEED, index + 1);
      let battle = null, diagnostic = null;
      try {
        let originals = [];
        if (mode === "bag") {
          const result = window.IRON_PIT_TEST_BAG_FIGHT.run(entry, seed);
          battle = result.replay.battle;
          diagnostic = result.replay.diagnostic_id;
        } else {
          originals = source(entry.selection).map(([, card]) =>
            [card, JSON.stringify(card)]);
          const result = turbo.runSeeded(entry.selection, seed);
          battle = result.battle;
          diagnostic = result.diagnostic_id;
        }
        const problems = inspect(battle, originals);
        // A raw, lossless transcript is written for EVERY completed fight,
        // not just failures, samples, first rounds, or observed abilities.
        await writer.fight(index, report.total, entry, seed, battle, diagnostic);
        if (problems.length) throw new Error(problems.join(", "));
        report.passed++;
        if (index % 25 === 0 || index === report.total - 1) {
          await window.IRON_PIT_BULK_COMBAT_UI.show(api, entry, battle,
            `Fight ${index + 1} of ${report.total}: ${entry.label}`);
          window.IRON_PIT_BULK_COMBAT_UI.lastBattle = battle;
        }
      } catch (error) {
        console.error("Real bulk combat case failed", {entry, index, seed, error});
        report.failed++;
        if (report.failure_samples.length < 50)
          report.failure_samples.push({case_number: index + 1, seed,
            label: entry.label, error: error?.message || String(error)});
        await writer.error(index, report.total, entry, seed, error);
        if (battle) {
          try {
            await window.IRON_PIT_BULK_COMBAT_UI.show(api, entry, battle, entry.label);
            window.IRON_PIT_BULK_COMBAT_UI.lastBattle = battle;
          } catch (displayError) {
            console.error("Failed matchup could not be displayed", displayError);
          }
        }
      }
      report.completed++;
      if (index % 20 === 0 || index === report.total - 1) {
        window.IRON_PIT_BULK_COMBAT_UI.progress(report, mode);
        await new Promise(resolve => setTimeout(resolve, 0));
      }
    }
  }
  function install(api) {
    try {
      if (!api?.state || !api.ensureRuleset || !api.load || !api.updateControls)
        throw new Error("Actual player battlefield controller is required.");
      async function start(mode) {
        if (control || api.state.fighting) return;
        const flag = {running: true, stopRequested: false};
        control = flag;
        api.state.fighting = true;
        $("bulk-bag").disabled = $("bulk-pairs").disabled = true;
        $("bulk-stop").disabled = false;
        let writer = null;
        let report = null;
        try {
          // User click opens the streaming destination BEFORE any planning awaits.
          writer = await window.IRON_PIT_BULK_COMBAT_FILE.open(mode, BASE_SEED);
          await api.ensureRuleset("2024", true);
          await api.ensureRuleset("2014", true);
          const plan = mode === "bag"
            ? window.IRON_PIT_TEST_BAG_PLAN.create()
            : await window.IRON_PIT_TEST_ALL_PLAN.create("pairs");
          report = {mode, seed: BASE_SEED,
            total: mode === "bag" ? plan.total * BAG_ATTEMPTS : plan.total,
            completed: 0, passed: 0, failed: 0, stopped: false,
            failure_samples: [], attempts_per_card: mode === "bag" ? BAG_ATTEMPTS : 1};
          window.IRON_PIT_BULK_COMBAT_UI.progress(report, mode);
          await execute(api, plan, mode, writer, report, flag);
        } catch (error) {
          console.error("Bulk suite or transcript stream failed", {mode, error});
          $("bulk-status").textContent = "Test stopped: " + (error?.message || String(error));
          if (report) report.fatal_error = error?.stack || String(error);
        } finally {
          if (report) { report.stopped = report.stopped || flag.stopRequested;
            report.skipped = report.total - report.completed; }
          if (writer) {
            try { await writer.close(report || {mode, fatal_error: "Plan unavailable"}); }
            catch (error) {
              console.error("Full combat log file close failed", error);
              $("bulk-status").textContent = "Log file could not be finalized: " + error.message;
            }
          }
          control = null;
          api.state.fighting = false;
          $("bulk-bag").disabled = $("bulk-pairs").disabled = false;
          $("bulk-stop").disabled = true;
          api.updateControls();
          if (report && !report.fatal_error)
            $("bulk-status").textContent += " · Full TXT transcript saved.";
        }
      }
      window.IRON_PIT_BULK_COMBAT_UI.install(start, () => {
        if (control) control.stopRequested = true;
      });
    } catch (error) {
      console.error("Bulk suite installation failed", error);
      throw error;
    }
  }
  window.IRON_PIT_BULK_COMBAT_RUNNER = {install, inspect, caseAt};
})();