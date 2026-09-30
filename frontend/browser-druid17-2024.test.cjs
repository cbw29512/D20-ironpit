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

const hero = window.IRON_PIT_BROWSER_HEROES["thalen-greenbough-l17"];
assert.ok(hero, "2024 Druid 17 must exist in generated browser heroes.");
assert.equal(hero.level, 17);
assert.equal(hero.max_hp, 88);
assert.equal(hero.ability_scores.wisdom, 20);
assert.equal(hero.ability_scores.charisma, 20);
assert.equal(hero.saving_throw_bonuses.wisdom, 11);
assert.equal(hero.saving_throw_bonuses.intelligence, 7);
assert.equal(hero.skill_bonuses.nature, 12);
assert.equal(hero.skill_bonuses.survival, 11);
assert.deepEqual(hero.resources, {
  "spell-slot-1": 4,
  "spell-slot-2": 3,
  "spell-slot-3": 3,
  "spell-slot-4": 3,
  "spell-slot-5": 2,
  "spell-slot-6": 1,
  "spell-slot-7": 1,
  "spell-slot-8": 1,
  "spell-slot-9": 1,
  "wild-shape": 4,
  "wild-resurgence-slot-restore": 1,
  "natural-recovery-free-cast": 1,
});
assert.equal(hero.canonical_prepared_spells.length, 19);
assert.equal(hero.canonical_prepared_spells.at(-1).id, "foresight");

const foresight = hero.defensive_spell_actions.find((item) => item.id === "foresight");
assert.ok(foresight, "Generated Druid 17 must expose Foresight.");
assert.equal(foresight.level, 9);
assert.equal(foresight.actionCost, "action");
assert.equal(foresight.range, 5);
assert.equal(foresight.durationMinutes, 480);
assert.equal(foresight.targetPolicy, "self");
assert.equal(foresight.concentration, false);
assert.equal(foresight.freeOpeningCast, true);
assert.deepEqual(
  new Set(foresight.modifierEffects.map((item) => item.kind)),
  new Set(["d20-test-advantage", "attacks-against-disadvantage"]),
);

console.log("Generated browser 2024 Druid 17 Foresight regressions passed.");
