"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(fs.readFileSync("frontend/browser-heroes.js", "utf8"), {
  filename: "browser-heroes.js",
});

const cleric = window.IRON_PIT_BROWSER_HEROES["seraphine-dawnshield-2014-l9"];
assert.ok(cleric);
assert.equal(cleric.name, "Seraphine Dawnshield");
assert.equal(cleric.level, 9);
assert.equal(cleric.max_hp, 84);
assert.equal(cleric.ability_scores.wisdom, 20);
assert.deepEqual(cleric.resources, {
  "channel-divinity": 2,
  "spell-slot-1": 4,
  "spell-slot-2": 3,
  "spell-slot-3": 3,
  "spell-slot-4": 3,
  "spell-slot-5": 1,
});

const upcast = cleric.spell_attack_actions.find((item) => item.id === "inflict-wounds-l5");
assert.ok(upcast);
assert.equal(upcast.name, "Inflict Wounds (5th-Level)");
assert.equal(upcast.level, 5);
assert.equal(upcast.damageDiceCount, 7);
assert.equal(upcast.damageDiceSize, 10);
assert.equal(upcast.damageType, "necrotic");

const mass = cleric.healingActions.find((item) => item.id === "mass-cure-wounds");
assert.ok(mass);
assert.equal(mass.range, 60);
assert.equal(mass.areaRadiusFt, 30);
assert.equal(mass.maxTargets, 6);
assert.equal(mass.diceCount, 3);
assert.equal(mass.diceSize, 8);
assert.equal(mass.healingBonus, 12);
assert.equal(mass.resourceId, "spell-slot-5");
assert.deepEqual(mass.excludedCreatureTypes, ["undead", "construct"]);

assert.deepEqual(
  cleric.canonical_always_prepared_spells.map((item) => item.id).slice(-2),
  ["mass-cure-wounds", "raise-dead"],
);

console.log("Browser persistent 2014 Life Cleric level 9 certification passed.");
