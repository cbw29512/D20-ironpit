"use strict";
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

const E = window.IRON_PIT_BROWSER_ENGINE;
const deterministicDice = () => ({
  roll: (sides) => sides,
  rollMany: (count, sides) => Array(count).fill(sides),
});
window.IRON_PIT_DICE = deterministicDice();

const mixed = E.runEncounter({
  ruleset: "2024",
  hero_ids: ["karnok-stoneward-l1", "srd-wolf"],
  monster_ids: ["srd-commoner", "seraphine-dawnshield-l1"],
});
assert.deepEqual(mixed.setup.heroes.map((item) => item.state.template.kind), ["character", "monster"]);
assert.deepEqual(mixed.setup.monsters.map((item) => item.state.template.kind), ["monster", "character"]);
assert.notEqual(mixed.outcome, "active");
assert.ok(mixed.events.some((event) => event.event_type === "attack"));

window.IRON_PIT_DICE = deterministicDice();
const monsterDuel = E.runEncounter({
  ruleset: "2024",
  hero_ids: ["srd-commoner"],
  monster_ids: ["srd-commoner"],
});
assert.notEqual(monsterDuel.outcome, "active");
assert.equal(monsterDuel.setup.heroes[0].state.template.kind, "monster");
assert.equal(monsterDuel.setup.monsters[0].state.template.kind, "monster");
assert.equal(monsterDuel.setup.hero_total_levels, 0);

window.IRON_PIT_DICE = deterministicDice();
const sixDragons = E.runEncounter({
  ruleset: "2024",
  hero_ids: Array(6).fill("srd-blue-dragon-wyrmling"),
  monster_ids: Array(6).fill("srd-blue-dragon-wyrmling"),
});
assert.equal(sixDragons.setup.heroes.length, 6);
assert.equal(sixDragons.setup.monsters.length, 6);
assert.notEqual(sixDragons.outcome, "active");
assert.equal(sixDragons.setup.hero_total_levels, 0);
console.log("Mixed-team browser combat, monster duel and 6v6 monster regression passed.");
