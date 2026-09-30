"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

load("browser-heroes.js");

const hero = window.IRON_PIT_BROWSER_HEROES["thalen-greenbough-l10"];
assert.ok(hero, "2024 Druid 10 must exist in generated browser heroes.");
assert.equal(hero.level, 10);
assert.equal(hero.max_hp, 53);
assert.equal(hero.ability_scores.wisdom, 20);
assert.deepEqual(hero.damage_resistances, ["fire"]);
assert.deepEqual(hero.condition_immunities, ["poisoned"]);
assert.deepEqual(hero.resources, {
  "spell-slot-1": 4,
  "spell-slot-2": 3,
  "spell-slot-3": 3,
  "spell-slot-4": 3,
  "spell-slot-5": 2,
  "wild-shape": 3,
  "wild-resurgence-slot-restore": 1,
  "natural-recovery-free-cast": 1,
});

assert.equal(hero.canonical_cantrips.length, 5);
assert.equal(hero.canonical_cantrips.at(-1).id, "thunderclap");
assert.equal(hero.canonical_prepared_spells.length, 15);
assert.equal(hero.canonical_prepared_spells.at(-1).id, "thunderwave");

const thunderclap = hero.spell_save_actions.find((item) => item.id === "thunderclap");
assert.ok(thunderclap, "Druid 10 must expose 2024 Thunderclap.");
assert.equal(thunderclap.level, 0);
assert.equal(thunderclap.saveAbility, "constitution");
assert.equal(thunderclap.damageDiceCount, 2);
assert.equal(thunderclap.damageDiceSize, 6);
assert.equal(thunderclap.damageBonus, 5);
assert.equal(thunderclap.damageType, "thunder");
assert.equal(thunderclap.successDamage, "none");
assert.deepEqual(thunderclap.area, {
  shape: "emanation", origin: "self", radius_ft: 5, length_ft: null, width_ft: null,
});

const thunderwave = hero.spell_save_actions.find((item) => item.id === "thunderwave");
assert.ok(thunderwave, "Druid 10 must expose 2024 Thunderwave.");
assert.equal(thunderwave.level, 1);
assert.equal(thunderwave.saveAbility, "constitution");
assert.equal(thunderwave.damageDiceCount, 2);
assert.equal(thunderwave.damageDiceSize, 8);
assert.equal(thunderwave.damageType, "thunder");
assert.equal(thunderwave.successDamage, "half");
assert.equal(thunderwave.upcastDicePerLevel, 1);
assert.equal(thunderwave.failedSavePushFt, 10);
assert.deepEqual(thunderwave.area, {
  shape: "cube", origin: "self", radius_ft: null, length_ft: 15, width_ft: null,
});

console.log("Generated browser 2024 Druid 10 progression regressions passed.");
