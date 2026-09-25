"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-heroes.js"), "utf8"),
  { filename: "browser-heroes.js" },
);

const level18 = window.IRON_PIT_BROWSER_HEROES["aurelia-brightshield-2014-l18"];
const hero = window.IRON_PIT_BROWSER_HEROES["aurelia-brightshield-2014-l19"];

assert.ok(level18, "Aurelia level 18 must remain exported");
assert.ok(hero, "Aurelia level 19 must be exported");
assert.equal(hero.level, 19);
assert.equal(hero.max_hp, 156);
assert.equal(hero.ability_scores.strength, 20);
assert.equal(hero.ability_scores.dexterity, 12);
assert.equal(hero.ability_scores.charisma, 20);
assert.equal(hero.initiative_bonus, 1);
assert.equal(hero.aura_radius_2014_ft, 30);
assert.equal(hero.aura_of_protection_2014_bonus, 5);
assert.equal(hero.sacred_weapon_2014_bonus, 5);
assert.equal(hero.skill_bonuses.persuasion, 11);
assert.equal(hero.saving_throw_bonuses.dexterity, 1);
assert.equal(hero.saving_throw_bonuses.charisma, 11);

assert.deepEqual(
  [1, 2, 3, 4, 5].map((level) => hero.resources[`spell-slot-${level}`]),
  [4, 3, 3, 3, 2],
);
assert.equal(hero.resources["lay-on-hands"], 95);
assert.equal(hero.resources["cleansing-touch"], 5);
assert.equal(hero.spell_save_actions[0].id, "flame-strike");
assert.equal(hero.spell_save_actions[0].dc, 19);
assert.equal(hero.canonical_prepared_spells.length, 14);
const raiseDead = hero.canonical_prepared_spells.find((spell) => spell.id === "raise-dead");
assert.ok(raiseDead);
assert.equal(raiseDead.level, 5);
assert.deepEqual(raiseDead.requiredCapabilities, ["arena-out-of-scope"]);

console.log("2014 Paladin level 19 split ASI and spell progression browser parity passed.");
