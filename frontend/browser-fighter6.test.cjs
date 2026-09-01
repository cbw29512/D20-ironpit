"use strict";

const assert = require("node:assert/strict");

const fighter = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l6"];
assert.ok(fighter, "generated Fighter 6 card must exist");
assert.equal(fighter.level, 6);
assert.equal(fighter.max_hp, 58);
assert.equal(fighter.armor_class, 17);
assert.equal(fighter.speed_ft, 30);
assert.equal(fighter.fighting_style, "Defense");
assert.equal(fighter.critical_hit_minimum, 19);
assert.equal(fighter.initiative_advantage, true);
assert.equal(fighter.athletics_advantage, true);
assert.equal(fighter.critical_move_fraction, 0.5);
assert.equal(fighter.tactical_shift_fraction, 0.5);
assert.deepEqual(fighter.weapon_masteries, ["flail", "javelin", "spear", "longsword"]);
assert.equal(fighter.saving_throw_bonuses.strength, 8);
assert.equal(fighter.saving_throw_bonuses.constitution, 6);
assert.equal(fighter.skill_bonuses.athletics, 8);
assert.deepEqual(fighter.resources, {
  "second-wind": 3,
  "action-surge": 1,
  "adrenaline-rush": 3,
  "relentless-endurance": 1,
});

const greatsword = fighter.attacks.find((attack) => attack.id === "karnok-greatsword");
const shortbow = fighter.attacks.find((attack) => attack.id === "karnok-shortbow");
assert.ok(greatsword);
assert.ok(shortbow);
assert.equal(greatsword.bonus, 8);
assert.equal(greatsword.damageBonus, 5);
assert.equal(shortbow.bonus, 4);
assert.equal(shortbow.damageBonus, 1);
assert.equal(fighter.attack_action.id, "extra-attack");
assert.deepEqual(fighter.attack_action.slots, [
  { attackIds: ["karnok-greatsword", "karnok-shortbow"], saveActionIds: [] },
  { attackIds: ["karnok-greatsword", "karnok-shortbow"], saveActionIds: [] },
]);

console.log("Generated browser Fighter 6 ASI regression passed.");
require("./browser-fighter7.test.cjs");
