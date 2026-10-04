"use strict";
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();
require("./browser-catalog.js"); require("./battle-lab.js"); require("./browser-turbo.js");
require("./combat-preset-recipes.js"); require("./combat-presets.js");
(async () => {
  const catalogs = {
    "2014": await IRON_PIT_BROWSER_CATALOG.buildCatalog("2014"),
    "2024": await IRON_PIT_BROWSER_CATALOG.buildCatalog("2024"),
  };
  const snapshot = {
    "2014": JSON.stringify(catalogs["2014"]),
    "2024": JSON.stringify(catalogs["2024"]),
  };
  const classes = { "2014": new Set(), "2024": new Set() };
  const sizes = new Set();
  const fired = [];
  for (const recipe of IRON_PIT_COMBAT_PRESETS.recipes) {
    const catalog = catalogs[recipe.ruleset];
    const { heroes, monsters, difficulty, adjusted } = IRON_PIT_COMBAT_PRESETS.resolve(recipe, catalog);
    heroes.forEach((card) => classes[recipe.ruleset].add(card.class_id));
    sizes.add(`${recipe.ruleset}:${heroes.length}v${monsters.length}`);
    assert.ok(heroes.length <= 6 && monsters.length <= 6, recipe.id);
    assert.ok(recipe.purpose.length > 10, recipe.id);
    assert.ok(recipe.aspects.length > 0, recipe.id);
    assert.ok(Object.isFrozen(recipe) && Object.isFrozen(recipe.classes) && Object.isFrozen(recipe.monsters));
    const selection = {
      ruleset: recipe.ruleset,
      hero_ids: heroes.map((card) => card.runnable_template_id),
      monster_ids: monsters.map((card) => card.runnable_template_id),
      opening_conditions: (recipe.openingConditions || []).map((item) => ({
        side: item.side, roster_index: item.rosterIndex, condition_id: item.conditionId,
        source_side: item.sourceSide, source_roster_index: item.sourceRosterIndex,
      })),
    };
    const { battle } = IRON_PIT_BROWSER_TURBO.runSeeded(selection, recipe.seed);
    assert.ok(battle.events.length > 0, recipe.id);
    assert.ok(["heroes_win", "monsters_win", "draw"].includes(battle.outcome), `${recipe.id} ${battle.outcome}`);
    assert.equal(battle.setup.heroes.length, heroes.length);
    assert.equal(battle.setup.monsters.length, monsters.length);
    const banned = /teleport|plane.?shift|dimension-door|misty-step|summon|flies vertically/i;
    for (const event of battle.events) {
      assert.doesNotMatch(
        `${event.feature_id || ""} ${event.description || ""}`,
        banned,
        `${recipe.id} seed ${recipe.seed} used a pit-banned option: ${event.feature_id || event.description}`,
      );
    }
    for (const spec of recipe.aspects) {
      assert.ok(
        IRON_PIT_COMBAT_PRESETS.aspectFired(battle, spec),
        `${recipe.id} seed ${recipe.seed} missed ${spec.kind}:${Array.isArray(spec.value) ? spec.value.join("|") : spec.value}`,
      );
    }
    fired.push(`${recipe.id}@${recipe.seed}:${recipe.aspects.map((spec) => spec.kind).join("+")}`);
    if (recipe.id === "goblins") { assert.equal(difficulty, "Medium"); assert.equal(adjusted, 200); }
    if (recipe.id === "party") { assert.equal(difficulty, "Hard"); assert.equal(adjusted, 26100); }
  }
  assert.equal(classes["2014"].size, 12);
  assert.equal(classes["2024"].size, 12);
  for (const size of ["1v1", "1v2", "2v2", "3v3", "4v4", "5v5", "6v6"]) {
    assert.ok(sizes.has(`2014:${size}`), size);
    assert.ok(sizes.has(`2024:${size}`), `2024 ${size}`);
  }
  assert.equal(JSON.stringify(catalogs["2014"]), snapshot["2014"], "fights must never mutate 2014 preset source cards");
  assert.equal(JSON.stringify(catalogs["2024"]), snapshot["2024"], "fights must never mutate 2024 preset source cards");
  console.log(`${IRON_PIT_COMBAT_PRESETS.recipes.length} presets passed aspect seeds; ${fired.join(" | ")}`);
})().catch((error) => { console.error("Combat preset regression failed", error); process.exitCode = 1; });
