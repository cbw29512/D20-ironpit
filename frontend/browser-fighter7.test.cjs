"use strict";

const assert = require("node:assert/strict");

const H = window.IRON_PIT_BROWSER_HEROES;
const S = window.IRON_PIT_BROWSER_STATE;
const R = window.IRON_PIT_BROWSER_ROLLS;
const fighter = H["karnok-stoneward-l7"];
assert.ok(fighter, "generated Fighter 7 card must exist");
assert.equal(fighter.level, 7);
assert.equal(fighter.max_hp, 67);
assert.equal(fighter.great_weapon_fighting, true);
assert.equal(fighter.critical_hit_minimum, 19);
assert.equal(fighter.tactical_shift_fraction, 0.5);

const greatsword = fighter.attacks.find((attack) => attack.id === "karnok-greatsword");
const shortbow = fighter.attacks.find((attack) => attack.id === "karnok-shortbow");
assert.ok(greatsword);
assert.ok(shortbow);
assert.equal(greatsword.bonus, 8);
assert.equal(greatsword.damageBonus, 5);
assert.equal(greatsword.damageDieMinimum, 3);
assert.equal(shortbow.bonus, 4);
assert.equal(shortbow.damageBonus, 1);
assert.equal(shortbow.damageDieMinimum, undefined);

function setDice(values) {
  const queue = [...values];
  window.IRON_PIT_DICE = {
    roll: (sides) => {
      assert.ok(queue.length, `fixed dice exhausted before d${sides}`);
      const value = queue.shift();
      assert.ok(value >= 1 && value <= sides, `${value} is invalid for d${sides}`);
      return value;
    },
    rollMany: (count, sides) => Array.from({ length: count }, () => window.IRON_PIT_DICE.roll(sides)),
  };
}

{
  const state = S.buildState(structuredClone(fighter));
  state.feature_last_turn_keys["savage-attacker"] = "used";
  setDice([1, 2]);
  const damage = R.weaponDamage(state, greatsword, false, "normal", "used");
  assert.equal(damage.roll.total, 11);
  assert.deepEqual(damage.components[0].rolls, [3, 3]);
}

{
  const state = S.buildState(structuredClone(fighter));
  state.feature_last_turn_keys["savage-attacker"] = "used";
  setDice([1, 2, 1, 2]);
  const damage = R.weaponDamage(state, greatsword, true, "normal", "used");
  assert.equal(damage.roll.total, 17);
  assert.deepEqual(damage.components[0].rolls, [3, 3, 3, 3]);
}

{
  const state = S.buildState(structuredClone(fighter));
  state.feature_last_turn_keys["savage-attacker"] = "used";
  setDice([1]);
  const damage = R.weaponDamage(state, shortbow, false, "normal", "used");
  assert.equal(damage.roll.total, 2);
  assert.deepEqual(damage.components[0].rolls, [1]);
}

{
  const state = S.buildState(structuredClone(fighter));
  setDice([1, 2, 1, 6]);
  const damage = R.weaponDamage(state, greatsword, false, "normal", "turn-1:karnok");
  assert.equal(damage.roll.total, 14);
  assert.deepEqual(damage.components[0].rolls, [3, 6]);
  assert.equal(state.feature_last_turn_keys["savage-attacker"], "turn-1:karnok");
}

console.log("Generated browser Fighter 7 Great Weapon Fighting regressions passed.");
