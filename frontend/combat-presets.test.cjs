"use strict";
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();
require("./browser-catalog.js"); require("./battle-lab.js"); require("./browser-turbo.js"); require("./combat-presets.js");
(async () => {
  const template = Object.values(IRON_PIT_BROWSER_HEROES).find((hero) => hero.ruleset === "2014" && hero.class_id === "fighter" && hero.level === 5);
  const priorDice = IRON_PIT_DICE;
  for (const round of [1, 101]) {
    const state = IRON_PIT_BROWSER_STATE.buildState(template);
    assert.equal(state.current_round, null); state.current_round = round;
    state.active_d20_bonus_dice = [{ source_id: "bard", source_effect_id: "bardic-inspiration", source_name: "Bardic Inspiration", dice_count: 1, dice_size: 8, test_kinds: ["saving_throw"], applied_round: 1, expires_round: 101 }];
    const dice = [1, 8]; window.IRON_PIT_DICE = { ...priorDice, roll: () => dice.shift() };
    IRON_PIT_BROWSER_CONCENTRATION.start(state, "fighter", "test", 1);
    const result = IRON_PIT_BROWSER_CONCENTRATION.resolveDamage(state, 1);
    assert.equal(result.succeeded, round === 1);
    assert.equal(state.active_d20_bonus_dice.length, 0);
  }
  window.IRON_PIT_DICE = priorDice;
  const catalog = await IRON_PIT_BROWSER_CATALOG.buildCatalog("2014");
  const classes = new Set(), sizes = new Set(), events = new Set();
  const snapshot = JSON.stringify(catalog);
  for (const recipe of IRON_PIT_COMBAT_PRESETS.recipes) {
    const { heroes, monsters, difficulty, adjusted } = IRON_PIT_COMBAT_PRESETS.resolve(recipe, catalog);
    heroes.forEach((card) => classes.add(card.class_id)); sizes.add(`${heroes.length}v${monsters.length}`);
    assert.ok(heroes.length <= 6 && monsters.length <= 6);
    assert.ok(recipe.purpose.length > 40);
    assert.ok(Object.isFrozen(recipe) && Object.isFrozen(recipe.classes) && Object.isFrozen(recipe.monsters));
    const selection = { ruleset: "2014", hero_ids: heroes.map((card) => card.runnable_template_id), monster_ids: monsters.map((card) => card.runnable_template_id) };
    for (const seed of [1701, 1702, 1703]) {
      const { battle } = IRON_PIT_BROWSER_TURBO.runSeeded(selection, seed);
      assert.ok(battle.events.length > 0, recipe.id);
      assert.ok(["heroes_win", "monsters_win", "draw"].includes(battle.outcome), recipe.id);
      assert.equal(battle.setup.heroes.length, heroes.length);
      assert.equal(battle.setup.monsters.length, monsters.length);
      battle.events.forEach((event) => events.add(event.event_type));
    }
    if (recipe.id === "goblins") { assert.equal(difficulty, "Medium"); assert.equal(adjusted, 200); }
    if (recipe.id === "party") { assert.equal(difficulty, "Hard"); assert.equal(adjusted, 26100); }
  }
  assert.equal(classes.size, 12);
  for (const size of ["1v1", "1v2", "2v2", "3v3", "4v4", "5v5", "6v6"]) assert.ok(sizes.has(size), size);
  assert.equal(JSON.stringify(catalog), snapshot, "fights must never mutate preset source cards");
  console.log(`12 presets, 36 canonical fights passed; observed events: ${[...events].sort().join(", ")}`);
})().catch((error) => { console.error("Combat preset regression failed", error); process.exitCode = 1; });
