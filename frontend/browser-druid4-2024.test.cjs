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
load("browser-spell-modifiers.js");

const hero = window.IRON_PIT_BROWSER_HEROES["thalen-greenbough-l4"];
assert.ok(hero, "2024 Druid 4 must exist in generated browser heroes.");
assert.equal(hero.level, 4);
assert.equal(hero.max_hp, 23);
assert.equal(hero.ability_scores.wisdom, 19);
assert.equal(hero.saving_throw_bonuses.wisdom, 6);
assert.equal(hero.skill_bonuses.nature, 7);
assert.equal(hero.skill_bonuses.survival, 6);
assert.equal(hero.skill_bonuses.perception, 6);
assert.deepEqual(hero.resources, {
  "spell-slot-1": 4,
  "spell-slot-2": 3,
  "wild-shape": 2,
});
assert.deepEqual(hero.canonical_cantrips.map((spell) => spell.id), [
  "poison-spray", "elementalism", "mending", "starry-wisp",
]);
assert.deepEqual(hero.canonical_prepared_spells.map((spell) => spell.id), [
  "healing-word", "cure-wounds", "longstrider", "detect-magic",
  "faerie-fire", "lesser-restoration", "detect-poison-disease",
]);

const starry = hero.spell_attack_actions.find((spell) => spell.id === "starry-wisp");
assert.ok(starry);
assert.equal(starry.attackBonus, 6);
assert.equal(starry.range, 60);
assert.equal(starry.damageDiceCount, 1);
assert.equal(starry.damageDiceSize, 8);
assert.equal(starry.damageType, "radiant");
assert.equal(starry.onHitModifierEffects.length, 1);
const rider = starry.onHitModifierEffects[0];
assert.equal(rider.kind, "invisibility-benefits-suppressed");
assert.equal(rider.expiresAfterSourceTurns, 1);

const modifier = window.IRON_PIT_BROWSER_SPELL_MODIFIERS.build(
  "druid", "target", starry, rider, 0, 1,
);
assert.equal(modifier.kind, "invisibility-benefits-suppressed");
assert.equal(modifier.source_effect_id, "starry-wisp");
assert.equal(modifier.expires_source_turn_end_round, 2);

assert.equal(hero.saving_throw_actions[0].dc, 14);
assert.ok(hero.spell_save_actions.every((spell) => spell.dc === 14));
assert.equal(hero.replacement_form_actions[0].temporaryHpOnEnter, 4);

console.log("Generated browser 2024 Druid 4 ASI and Starry Wisp regressions passed.");
