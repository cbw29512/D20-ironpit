"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

load("browser-heroes.js");
load("browser-2014-monk.js");

const hero = Object.values(window.IRON_PIT_BROWSER_HEROES)
  .find((item) => item.id === "kael-stillwater-2014-l19");

assert.ok(hero, "certified 2014 Monk level 19 must be exported");
assert.deepEqual(hero.ability_scores, {
  strength: 14, dexterity: 20, constitution: 14,
  intelligence: 11, wisdom: 20, charisma: 9,
});
assert.equal(hero.armor_class, 20);
assert.equal(hero.max_hp, 136);
assert.equal(hero.speed_ft, 60);
assert.equal(hero.initiative_bonus, 5);
assert.equal(hero.resources.ki, 19);
assert.equal(hero.resources["wholeness-of-body"], 1);
assert.equal(hero.saving_throw_bonuses.strength, 8);
assert.equal(hero.saving_throw_bonuses.wisdom, 11);
assert.equal(hero.skill_bonuses.insight, 11);
assert.ok(hero.attacks.every((attack) => attack.bonus === 11));
assert.equal(hero.deferred_save_effect.save_dc, 19);
assert.equal(hero.opening_targeting_ward.save_dc, 19);

const state = { template: hero };
assert.equal(window.IRON_PIT_BROWSER_MONK_2014.monkDc(state), 19);

console.log("2014 Monk level 19 ASI and derived browser combat values are certified.");
