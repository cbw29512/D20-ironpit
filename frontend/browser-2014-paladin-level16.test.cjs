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

const hero = window.IRON_PIT_BROWSER_HEROES["aurelia-brightshield-2014-l16"];
assert.ok(hero, "Aurelia level 16 must be exported to the browser roster");

assert.equal(hero.level, 16);
assert.equal(hero.ability_scores.strength, 20);
assert.equal(hero.ability_scores.charisma, 19);
assert.equal(hero.max_hp, 132);
assert.equal(hero.aura_of_protection_2014_bonus, 4);
assert.equal(hero.sacred_weapon_2014_bonus, 4);
assert.equal(hero.skill_bonuses.persuasion, 9);
assert.equal(hero.resources["cleansing-touch"], 4);
assert.equal(hero.resources["lay-on-hands"], 80);
assert.deepEqual(
  [1, 2, 3, 4].map((level) => hero.resources[`spell-slot-${level}`]),
  [4, 3, 3, 2],
);

assert.equal(hero.passive_modifier_grants.length, 3);
assert.ok(hero.passive_modifier_grants.every((item) => item.source_id === "purity-of-spirit"));

const preparedIds = new Set(hero.canonical_prepared_spells.map((spell) => spell.id));
assert.equal(hero.canonical_prepared_spells.length, 12);
assert.equal(preparedIds.has("find-steed"), true);
assert.equal(preparedIds.has("create-food-and-water"), true);
assert.equal(preparedIds.has("death-ward"), true);
assert.equal(preparedIds.has("purify-food-and-drink"), false);

console.log("2014 Paladin level 16 incremental ASI parity passed.");
