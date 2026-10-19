(() => {
  "use strict";
  function selection(recipe, catalog, presets) {
    const cards = presets.resolve(recipe, catalog);
    return {
      ruleset: recipe.ruleset,
      hero_ids: cards.heroes.map((card) => card.runnable_template_id),
      monster_ids: cards.monsters.map((card) => card.runnable_template_id),
    };
  }
  async function rosterSweep(w, editions) {
    const cases = [];
    for (const ruleset of editions) {
      const catalog = await w.IRON_PIT_BROWSER_CATALOG.buildCatalog(ruleset);
      const heroes = catalog.heroes.filter((card) =>
        card.coverage_status === "raw_ready" && card.runnable_template_id);
      const monsters = catalog.monsters.filter((card) =>
        card.coverage_status === "raw_ready" && card.runnable_template_id);
      if (!heroes.length || !monsters.length) throw Error("No runnable " + ruleset + " roster.");
      const total = Math.max(heroes.length, monsters.length);
      for (let i = 0; i < total; i++) {
        const hero = heroes[i % heroes.length], monster = monsters[i % monsters.length];
        cases.push({ id: "roster-" + ruleset + "-" + (i + 1), ruleset,
          title: hero.name + " vs " + monster.name, seed: (1701 + i) >>> 0,
          aspects: [], selection: { ruleset, hero_ids: [hero.runnable_template_id],
            monster_ids: [monster.runnable_template_id] } });
      }
    }
    return cases;
  }
  function validate(replay, recipe, presets, expectedAspects) {
    const battle = replay.battle;
    if (!battle || !Array.isArray(battle.events) || battle.events.length < 1) throw Error("No battle events");
    if (!["heroes_win", "monsters_win", "draw"].includes(battle.outcome)) throw Error("Invalid outcome");
    if (!Number.isInteger(battle.rounds) || battle.rounds < 1 || battle.rounds > 100) throw Error("Invalid round count");
    if (battle.outcome === "draw" && battle.rounds >= 100) throw Error("Safety stop at 100 rounds");
    if (expectedAspects) {
      for (const spec of recipe.aspects) {
        if (!presets.aspectFired(battle, spec)) {
          throw Error("Missing expected " + spec.kind + ": " + JSON.stringify(spec.value));
        }
      }
    }
    return battle.rounds + " rounds, " + battle.events.length + " events, " + battle.outcome;
  }

  window.IRON_PIT_BETA_GAUNTLET_CASES = { selection, rosterSweep, validate };
})();
