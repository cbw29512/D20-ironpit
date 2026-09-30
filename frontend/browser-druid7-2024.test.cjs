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

const hero = window.IRON_PIT_BROWSER_HEROES["thalen-greenbough-l7"];
assert.ok(hero, "2024 Druid 7 must exist in generated browser heroes.");
assert.equal(hero.level, 7);
assert.equal(hero.max_hp, 38);
assert.equal(hero.ability_scores.wisdom, 19);
assert.equal(hero.saving_throw_bonuses.wisdom, 7);
assert.deepEqual(hero.resources, {
  "spell-slot-1": 4,
  "spell-slot-2": 3,
  "spell-slot-3": 3,
  "spell-slot-4": 1,
  "wild-shape": 3,
  "wild-resurgence-slot-restore": 1,
  "natural-recovery-free-cast": 1,
});

assert.equal(hero.canonical_prepared_spells.length, 11);
assert.equal(hero.canonical_prepared_spells.at(-1).id, "divination");

for (const id of ["poison-spray", "fire-bolt", "starry-wisp"]) {
  const cantrip = hero.spell_attack_actions.find((spell) => spell.id === id);
  assert.ok(cantrip, `${id} must be a generated Druid cantrip action.`);
  assert.equal(cantrip.damageDiceCount, 2);
  assert.equal(cantrip.damageBonus, 4);
}

const blight = hero.spell_save_actions.find((spell) => spell.id === "blight");
assert.ok(blight, "Arid Druid 7 must expose 2024 Blight.");
assert.equal(blight.level, 4);
assert.equal(blight.range, 30);
assert.equal(blight.saveAbility, "constitution");
assert.equal(blight.damageDiceCount, 8);
assert.equal(blight.damageDiceSize, 8);
assert.equal(blight.damageType, "necrotic");
assert.equal(blight.successDamage, "half");
assert.equal(blight.upcastDicePerLevel, 1);
assert.deepEqual(blight.automaticFailureCreatureTypes, ["Plant"]);

console.log("Generated browser 2024 Druid 7 Potent Spellcasting and Blight regressions passed.");
