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

const hero = window.IRON_PIT_BROWSER_HEROES["thalen-greenbough-l9"];
assert.ok(hero, "2024 Druid 9 must exist in generated browser heroes.");
assert.equal(hero.level, 9);
assert.equal(hero.max_hp, 48);
assert.equal(hero.ability_scores.wisdom, 20);
assert.equal(hero.ability_scores.charisma, 16);
assert.equal(hero.saving_throw_bonuses.wisdom, 9);
assert.deepEqual(hero.resources, {
  "spell-slot-1": 4,
  "spell-slot-2": 3,
  "spell-slot-3": 3,
  "spell-slot-4": 3,
  "spell-slot-5": 1,
  "wild-shape": 3,
  "wild-resurgence-slot-restore": 1,
  "natural-recovery-free-cast": 1,
});

assert.equal(hero.canonical_prepared_spells.length, 14);
assert.deepEqual(
  hero.canonical_prepared_spells.slice(-2).map((item) => item.id),
  ["cone-of-cold", "mass-cure-wounds"],
);

const cone = hero.spell_save_actions.find((item) => item.id === "cone-of-cold");
assert.ok(cone, "Druid 9 must expose 2024 Cone of Cold.");
assert.equal(cone.level, 5);
assert.equal(cone.saveAbility, "constitution");
assert.equal(cone.damageDiceCount, 8);
assert.equal(cone.damageDiceSize, 8);
assert.equal(cone.damageType, "cold");
assert.equal(cone.successDamage, "half");
assert.deepEqual(cone.area, {
  shape: "cone", origin: "self", radius_ft: null, length_ft: 60, width_ft: null,
});

const mass = hero.healing_actions.find((item) => item.id === "mass-cure-wounds");
assert.ok(mass, "Druid 9 must expose Mass Cure Wounds.");
assert.equal(mass.range, 60);
assert.equal(mass.areaRadiusFt, 30);
assert.equal(mass.maxTargets, 6);
assert.equal(mass.diceCount, 5);
assert.equal(mass.diceSize, 8);
assert.equal(mass.healingBonus, 5);

const wall = hero.persistent_barrier_actions.find((item) => item.id === "wall-of-stone");
assert.ok(wall, "Druid 9 must expose Wall of Stone.");
assert.equal(wall.level, 5);
assert.equal(wall.castRangeFt, 120);
assert.equal(wall.concentration, true);
assert.equal(wall.durationRounds, 100);
assert.equal(wall.permanentAfterFullDuration, true);
assert.equal(wall.minSections, 10);
assert.equal(wall.maxSections, 10);
assert.equal(wall.sectionsMustBeContiguous, true);
assert.equal(wall.sectionLengthFt, 10);
assert.equal(wall.sectionHeightFt, 10);
assert.equal(wall.sectionThicknessInches, 6);
assert.equal(wall.armorClass, 15);
assert.equal(wall.hitPointsPerSection, 180);
assert.deepEqual(wall.damageImmunities, ["poison", "psychic"]);
assert.equal(wall.requiredSupportMaterial, "stone");

console.log("Generated browser 2024 Druid 9 progression regressions passed.");
