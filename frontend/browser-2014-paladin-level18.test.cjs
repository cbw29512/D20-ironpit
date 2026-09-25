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

const level17 = window.IRON_PIT_BROWSER_HEROES["aurelia-brightshield-2014-l17"];
const hero = window.IRON_PIT_BROWSER_HEROES["aurelia-brightshield-2014-l18"];

assert.ok(level17, "Aurelia level 17 must remain exported");
assert.ok(hero, "Aurelia level 18 must be exported to the browser roster");
assert.equal(hero.level, 18);
assert.equal(hero.max_hp, 148);
assert.deepEqual(hero.ability_scores, level17.ability_scores);
assert.deepEqual(
  [1, 2, 3, 4, 5].map((level) => hero.resources[`spell-slot-${level}`]),
  [4, 3, 3, 3, 1],
);
assert.equal(hero.resources["lay-on-hands"], 90);
assert.equal(hero.resources["cleansing-touch"], 4);
assert.equal(level17.aura_radius_2014_ft, 10);
assert.equal(hero.aura_radius_2014_ft, 30);
assert.equal(hero.aura_of_protection_2014_bonus, 4);
assert.equal(hero.aura_of_devotion_2014, true);
assert.equal(hero.aura_of_courage_2014, true);
assert.deepEqual(hero.spell_save_actions, level17.spell_save_actions);
assert.deepEqual(hero.passive_modifier_grants, level17.passive_modifier_grants);
assert.equal(hero.canonical_prepared_spells.length, 13);
const locateObject = hero.canonical_prepared_spells.find((spell) => spell.id === "locate-object");
assert.ok(locateObject);
assert.equal(locateObject.level, 2);
assert.deepEqual(locateObject.requiredCapabilities, ["arena-out-of-scope"]);

console.log("2014 Paladin level 18 aura-expansion browser parity passed.");
