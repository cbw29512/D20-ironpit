(() => {
  "use strict";

  // Runtime state: {completed, passed, failed, skipped, by_edition,
  // failures, observed, warnings, stopped}. One source case = one real fight.
  const OUTCOMES = new Set(["heroes_win", "monsters_win", "draw"]);

  function sources(selection) {
    try {
      const heroes = window.IRON_PIT_BROWSER_HEROES || {};
      const monsters = selection.ruleset === "2014"
        ? window.IRON_PIT_BROWSER_MONSTERS_2014 || {}
        : window.IRON_PIT_BROWSER_MONSTERS || {};
      return [...new Set([...selection.hero_ids, ...selection.monster_ids])]
        .map(id => {
          const card = heroes[id] || monsters[id];
          if (!card || card.ruleset !== selection.ruleset)
            throw new Error(`Missing playable ${selection.ruleset} source card: ${id}`);
          return [id, card];
        });
    } catch (error) {
      console.error("Test All source card lookup failed", {selection, error});
      throw error;
    }
  }

  function aggregate(totals, events) {
    try {
      for (const event of events) {
        const add = (group, name) => {
          if (typeof name === "string" && name)
            group[name] = (group[name] || 0) + 1;
        };
        add(totals.event_types, event.event_type);
        add(totals.feature_ids, event.feature_id);
        for (const id of event.applied_condition_ids || []) add(totals.conditions, id);
        for (const item of event.damage_components || [])
          add(totals.damage_types, item.damage_type);
      }
    } catch (error) {
      console.error("Failed to tally observed combat evidence", error);
      throw error;
    }
  }

  async function run(plan, baseSeed, control, onProgress = () => {}) {
    if (!Number.isInteger(baseSeed) || baseSeed < 1 || baseSeed > 0xffffffff)
      throw new RangeError("Full-sweep seed must be a positive uint32.");
    const turbo = window.IRON_PIT_BROWSER_TURBO;
    const lab = window.IRON_PIT_BATTLE_LAB;
    if (!turbo?.runSeeded || !turbo?.deriveSeed || !lab?.fingerprint)
      throw new Error("Shared seeded combat runtime is not available.");
    const reporter = window.IRON_PIT_TEST_ALL_REPORT;
    if (!reporter?.create || !reporter?.failure || !reporter?.advance)
      throw new Error("Bounded Test All evidence recorder is missing.");
    const startIndex = control.startIndex ?? 0;
    const result = reporter.create(plan, baseSeed, startIndex);
    try {
      for (let index = startIndex; index < plan.total; index += 1) {
        if (control.stopRequested) { result.stopped = true; break; }
        const entry = plan.at(index);
        const edition = entry.selection.ruleset;
        const seed = entry.kind === "preset"
          ? entry.seed : turbo.deriveSeed(baseSeed, index + 1);
        const problems = [];
        let replay = null;
        try {
          const cards = sources(entry.selection);
          const before = cards.map(([id, card]) => [id, JSON.stringify(card)]);
          replay = turbo.runSeeded(entry.selection, seed);
          const battle = replay.battle, events = battle?.events;
          if (!Array.isArray(events) || !events.length)
            problems.push("no_combat_events");
          if (!OUTCOMES.has(battle?.outcome))
            problems.push("missing_final_outcome");
          if (events?.some(event => event.event_type === "movement"))
            problems.push("forbidden_tactical_movement");
          if (before.some(([id, snapshot], i) =>
            id !== cards[i][0] || snapshot !== JSON.stringify(cards[i][1])))
            problems.push("source_card_mutation");
          if (entry.required_aspects?.some(aspect =>
            !window.IRON_PIT_COMBAT_PRESETS.aspectFired(battle, aspect)))
            problems.push("preset_required_mechanic_not_observed");
          if (entry.kind === "preset" &&
            lab.fingerprint(battle) !== lab.fingerprint(
              turbo.runSeeded(entry.selection, seed).battle))
            problems.push("seed_replay_mismatch");
          if (battle.outcome === "draw" && battle.rounds >= 100)
            result.warnings += 1;
          aggregate(result.observed, events || []);
        } catch (error) {
          // Reporter logs only one example per error class to avoid
          // exhausting the browser console during a very large sweep.
          problems.push(`engine_error: ${error?.message || String(error)}`);
        }
        if (problems.length) reporter.failure(result, entry, index, seed, problems, replay);
        else result.by_edition[edition].passed += 1;
        reporter.advance(result, index, problems);
        if (result.completed % 20 === 0 || result.completed === plan.total) {
          try { onProgress(result); }
          catch (error) { console.error("Test All progress display failed", error); }
          await new Promise(resolve => setTimeout(resolve, 0));
        }
      }
      result.skipped = result.total - result.processed;
      try { onProgress(result); }
      catch (error) { console.error("Final Test All status could not be displayed", error); }
      return result;
    } catch (error) {
      console.error("Full roster test sweep aborted unexpectedly", error);
      throw error;
    }
  }

  window.IRON_PIT_TEST_ALL_RUNNER = {run, sources};
})();
