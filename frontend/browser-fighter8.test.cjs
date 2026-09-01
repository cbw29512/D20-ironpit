"use strict";

const assert = require("node:assert/strict");

const fighter = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l8"];
assert.ok(fighter, "generated Fighter 8 card must exist");
assert.equal(fighter.level, 8);
assert.equal(fighter.max_hp, 84);
assert.equal(fighter.armor_class, 17);
assert.equal(fighter.speed_ft, 30);
assert.equal(fighter.saving_throw_bonuses.strength, 8);
assert.equal(fighter.saving_throw_bonuses.constitution, 7);
assert.equal(fighter.skill_bonuses.athletics, 8);
assert.equal(fighter.great_weapon_fighting, true);
assert.equal(fighter.critical_hit_minimum, 19);
assert.equal(fighter.tactical_shift_fraction, 0.5);
assert.deepEqual(fighter.resources, {
  "second-wind": 3,
  "action-surge": 1,
  "adrenaline-rush": 3,
  "relentless-endurance": 1,
});

const greatsword = fighter.attacks.find((attack) => attack.id === "karnok-greatsword");
const shortbow = fighter.attacks.find((attack) => attack.id === "karnok-shortbow");
assert.equal(greatsword.bonus, 8);
assert.equal(greatsword.damageBonus, 5);
assert.equal(greatsword.damageDieMinimum, 3);
assert.equal(shortbow.bonus, 4);
assert.equal(shortbow.damageBonus, 1);
assert.equal(shortbow.damageDieMinimum, undefined);
assert.equal(fighter.attack_action.slots.length, 2);

console.log("Generated browser Fighter 8 Constitution ASI regression passed.");
