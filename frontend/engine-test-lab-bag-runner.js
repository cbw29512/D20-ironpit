(() => {
  "use strict";
  const OUTCOMES = new Set(["heroes_win", "monsters_win", "draw"]);
  const DELAY = () => new Promise(resolve => setTimeout(resolve, 0));

  // State: one result per source card, a bounded number of seeded attempts,
  // accumulated ability evidence, failures, and Stop/partial-export support.
  async function run(plan, seed, attemptsPerCard, control, progress = () => {}) {
    if (!Number.isInteger(seed) || seed < 1 || seed > 0xffffffff)
      throw new RangeError("Punching Bag seed must be a positive uint32.");
    if (!Number.isInteger(attemptsPerCard) || attemptsPerCard < 1 ||
        attemptsPerCard > 5) throw new RangeError("Choose 1–5 attempts per card.");
    const turbo = window.IRON_PIT_BROWSER_TURBO;
    const fight = window.IRON_PIT_TEST_BAG_FIGHT;
    const coverage = window.IRON_PIT_TEST_BAG_COVERAGE;
    if (!turbo?.deriveSeed || !fight?.run || !coverage?.declared)
      throw new Error("The shared Punching Bag combat suite is missing.");
    const report = {
      mode: "all_cards_vs_punching_bag", started_at: new Date().toISOString(),
      seed, attempts_per_card: attemptsPerCard,
      total: plan.total, completed: 0, passed: 0, failed: 0,
      stopped: false, skipped: 0, fights_executed: 0,
      by_edition: {"2014": {passed: 0, failed: 0},
        "2024": {passed: 0, failed: 0}},
      cases: [], failures: [],
      contract: "ACTUAL combat outcomes only; unobserved abilities are NOT certified.",
    };
    try {
      for (let index = 0; index < plan.total; index++) {
        if (control.stopRequested) { report.stopped = true; break; }
        const entry = plan.at(index), card = fight.sourceCard(entry);
        const declared = coverage.declared(card);
        const observed = new Map(), attempt_logs = [];
        const problems = [], branchTotals = {};
        for (let attempt = 0; attempt < attemptsPerCard; attempt++) {
          if (control.stopRequested) { report.stopped = true; break; }
          const testSeed = turbo.deriveSeed(seed, index * attemptsPerCard + attempt + 1);
          const detail = {seed: testSeed, attempt: attempt + 1};
          try {
            const {replay, source_actor_id, bag_actor_id} = fight.run(entry, testSeed);
            const battle = replay.battle, events = battle.events || [];
            detail.outcome = battle.outcome;
            detail.rounds = battle.rounds;
            detail.event_count = events.length;
            detail.diagnostic_id = replay.diagnostic_id;
            if (!OUTCOMES.has(battle.outcome)) problems.push("invalid_battle_outcome");
            if (!events.length) problems.push("no_combat_events");
            if (events.some(e => e.event_type === "movement"))
              problems.push("forbidden_tactical_movement");
            if (events.some(e => e.actor_id === bag_actor_id &&
                (e.damage_roll?.total || 0) > 0))
              problems.push("punching_bag_dealt_nonzero_damage");
            const evidence = coverage.audit(card, events, source_actor_id);
            for (const item of evidence.exercised)
              observed.set(`${item.category}:${item.id}`, item);
            for (const [key, count] of Object.entries(evidence.branches))
              branchTotals[key] = (branchTotals[key] || 0) + count;
            detail.ability_ids_seen = evidence.exercised.map(item => item.id);
            if (battle.outcome === "draw" && battle.rounds === 100)
              detail.round_limit = true; // Expected for 10,000-HP targets.
          } catch (error) {
            console.error("Punching Bag case attempt failed", {entry, testSeed, error});
            const message = `engine_error: ${error?.message || String(error)}`;
            problems.push(message);
            detail.error = message;
          }
          report.fights_executed++;
          attempt_logs.push(detail);
          // A whole-card audit can stop once every *active* declaration has
          // actual event evidence. Passive traits remain unverified separately.
          const pending = declared.filter(item => !item.source_only &&
            !observed.has(`${item.category}:${item.id}`));
          if (!pending.length) break;
        }
        const missing = declared.filter(item =>
          !observed.has(`${item.category}:${item.id}`));
        const result = {
          edition: entry.edition, kind: entry.source_kind,
          card_id: entry.source_id, card_name: card.name,
          declared: declared.length, observed: observed.size,
          not_observed: missing, branches: branchTotals,
          attempts: attempt_logs, problems: [...new Set(problems)],
        };
        report.cases.push(result);
        if (result.problems.length) {
          report.failed++;
          report.by_edition[entry.edition].failed++;
          report.failures.push(result);
        } else {
          report.passed++;
          report.by_edition[entry.edition].passed++;
        }
        report.completed++;
        try { progress(report); }
        catch (error) { console.error("Punching Bag progress display failed", error); }
        await DELAY();
      }
      report.skipped = report.total - report.completed;
      report.ended_at = new Date().toISOString();
      try { progress(report); }
      catch (error) { console.error("Punching Bag final progress failed", error); }
      return report;
    } catch (error) {
      console.error("Full monster/pregen Punching Bag sweep failed", error);
      throw error;
    }
  }
  window.IRON_PIT_TEST_BAG_RUNNER = {run};
})();
