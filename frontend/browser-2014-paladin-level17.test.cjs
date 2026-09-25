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

const hero = window.IRON_PIT_BROWSER_HEROES["aurelia-brightshield-2014-l17"];
assert.ok(hero, "Aurelia level 17 must be exported to the browser roster");
assert.equal(hero.level, 17);
assert.equal(hero.max_hp, 140);
assert.deepEqual(
  [1, 2, 3, 4, 5].map((level) => hero.resources[`spell-slot-${level}`]),
  [4, 3, 3, 3, 1],
);
assert.equal(hero.resources["lay-on-hands"], 85);
assert.equal(hero.resources["cleansing-touch"], 4);
assert.equal(hero.passive_modifier_grants.length, 3);

assert.equal(hero.spell_save_actions.length, 1);
const flame = hero.spell_save_actions[0];
assert.equal(flame.id, "flame-strike");
assert.equal(flame.level, 5);
assert.equal(flame.range, 60);
assert.equal(flame.areaRadius, 10);
assert.equal(flame.saveAbility, "dexterity");
assert.equal(flame.dc, 18);
assert.equal(flame.successDamage, "half");
assert.deepEqual(flame.damageComponents, [
  { diceCount: 4, diceSize: 6, damageBonus: 0, damageType: "fire" },
  { diceCount: 4, diceSize: 6, damageBonus: 0, damageType: "radiant" },
]);

const oathIds = new Set(hero.canonical_always_prepared_spells.map((spell) => spell.id));
assert.equal(oathIds.has("commune"), true);
assert.equal(oathIds.has("flame-strike"), true);
console.log("2014 Paladin level 17 Flame Strike browser parity passed.");
