(() => {
  "use strict";
  // Report schema: immutable metadata, one row per attempted pregen,
  // complete real-browser battle.events, coverage observations and violations.
  const OUTCOMES = new Set(["heroes_win", "monsters_win", "draw"]);
  function create(total, seed) {
    try {
      if (!Number.isInteger(total) || total < 1) throw new Error("No playable pregens to test.");
      return {
        mode: "battlefield_pregens_vs_punching_bag",
        engine: "IRON_PIT_EXECUTION.resolveReplay",
        presentation: "IRON_PIT_BATTLEFIELD_REPLAY.play(instant)",
        started_at: new Date().toISOString(),
        seed, total, completed: 0, passed: 0, failed: 0,
        stopped: false, skipped: 0, cases: [],
        contract: "A completed fight does not certify unobserved abilities.",
      };
    } catch (error) {
      console.error("Could not create battlefield gauntlet report", error);
      throw error;
    }
  }
  function record(report, entry, seed, session, sourceSnapshot) {
    try {
      const battle = session.battle;
      const events = battle?.events;
      if (!Array.isArray(events)) throw new Error("Missing production combat event array.");
      const source = window.IRON_PIT_BROWSER_HEROES?.[entry.runnable_template_id];
      if (!source || source.ruleset !== entry.ruleset)
        throw new Error("Certified pregen source missing or cross-edition.");
      const actor = battle.setup.heroes.find(item =>
        item.state.template.id === entry.runnable_template_id);
      const bag = battle.setup.monsters.find(item =>
        item.state.template.id === "custom-" + entry.ruleset + "-punching-bag");
      if (!actor || !bag || battle.setup.heroes.length !== 1 ||
          battle.setup.monsters.length !== 1)
        throw new Error("A Punching Bag test must be exactly one pregen versus one bag.");
      const problems = [];
      if (!OUTCOMES.has(battle.outcome)) problems.push("invalid_battle_outcome");
      if (!events.length) problems.push("no_combat_events");
      if (events.some(event => event.event_type === "movement"))
        problems.push("forbidden_tactical_movement");
      if (bag.state.template.armor_class !== 10 ||
          bag.state.template.max_hp !== 10000)
        problems.push("invalid_punching_bag_stats");
      if (events.some(event => event.actor_id === bag.combatant_id &&
          ((event.damage_roll?.total || 0) > 0 ||
           (event.damage_components || []).some(component => (component.applied_total || 0) > 0))))
        problems.push("punching_bag_dealt_damage");
      if (JSON.stringify(source) !== sourceSnapshot) problems.push("source_card_mutated");
      const abilities = window.IRON_PIT_TEST_BAG_COVERAGE.audit(
        source, events, actor.combatant_id);
      const row = {
        edition: entry.ruleset, card_id: entry.runnable_template_id,
        card_name: entry.name, level: entry.level,
        seed, diagnostic_id: session.diagnosticId, rounds: battle.rounds,
        outcome: battle.outcome, problems, abilities,
        event_count: events.length, events,
      };
      report.cases.push(row);
      report.completed += 1;
      if (problems.length) report.failed += 1;
      else report.passed += 1;
      return row;
    } catch (error) {
      console.error("Battlefield gauntlet case inspection failed", {entry, seed, error});
      return failure(report, entry, seed, error, session);
    }
  }
  function failure(report, entry, seed, error, session = null) {
    try {
      const row = {
        edition: entry.ruleset, card_id: entry.runnable_template_id,
        card_name: entry.name, level: entry.level, seed,
        problems: ["engine_error: " + (error?.message || String(error))],
        event_count: session?.battle?.events?.length || 0,
        events: session?.battle?.events || [], abilities: null,
        diagnostic_id: session?.diagnosticId || null,
      };
      report.cases.push(row);
      report.completed += 1;
      report.failed += 1;
      return row;
    } catch (caught) {
      console.error("Could not preserve gauntlet failure evidence", {entry, caught});
      throw caught;
    }
  }
  function finish(report, stopped) {
    try {
      report.stopped = Boolean(stopped);
      report.skipped = report.total - report.completed;
      report.ended_at = new Date().toISOString();
      return report;
    } catch (error) {
      console.error("Could not finalize battlefield gauntlet report", error);
      throw error;
    }
  }
  window.IRON_PIT_BATTLEFIELD_BAG_REPORT = {create, record, failure, finish};
})();