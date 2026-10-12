"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");

global.window = globalThis;
const load = (file) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, file), "utf8"), { filename: file },
);
window.IRON_PIT_DICE = {
  queue: [],
  roll(sides) {
    const value = this.queue.shift();
    if (!Number.isInteger(value) || value < 1 || value > sides) throw new Error("Invalid deterministic die");
    return value;
  },
  rollMany(count, sides) { return Array.from({ length: count }, () => this.roll(sides)); },
};
load("browser-timed-control-limits.js");
load("browser-once-per-turn-hit-damage.js");
load("browser-rolls.js");
const count = window.IRON_PIT_BROWSER_TIMED_CONTROL.registerTurnAttack;
const damage = window.IRON_PIT_BROWSER_ROLLS.weaponDamage;
const weapon = {
  name: "Club", kind: "melee", diceCount: 1, diceSize: 4,
  damageBonus: 0, damageType: "bludgeoning", onHitDamage: [],
};
const attacker = () => ({
  template: {
    max_hp: 20, traits: [],
    once_per_turn_weapon_hit_damage_rider: {
      source_id: "surprise-attack", source_name: "Surprise Attack",
      dice_count: 2, dice_size: 6, flat_bonus: 0, damage_type: null,
      requires_first_attack_of_fight: true,
      requires_attacker_first_turn: true,
      requires_target_unacted: true,
    },
  },
  current_hp: 20, turns_started: 1, attacks_this_turn: 0,
  feature_last_turn_keys: {}, feature_use_counts: {},
});
const target = () => ({ current_hp: 20, turns_started: 0, template: { max_hp: 20 } });
const swing = (a, t, rolls, critical = false) => {
  window.IRON_PIT_DICE.queue = [...rolls];
  const result = damage(a, weapon, critical, "normal", "1:bugbear", null, t);
  assert.equal(window.IRON_PIT_DICE.queue.length, 0);
  return result.components;
};

// Winning initiative qualifies only the first attack attempt.
{
  const a = attacker(), t = target();
  count(a);
  const result = swing(a, t, [2, 3, 4]);
  assert.deepEqual(result.map((part) => part.source), ["Club", "Surprise Attack"]);
  assert.deepEqual(result[1].rolls, [3, 4]);
  assert.equal(result[1].damage_type, "bludgeoning");
  assert.equal(a.feature_use_counts.weapon_attack_attempts, 1);
}
// Missing the first attack still consumes the one opening opportunity.
{
  const a = attacker(), t = target();
  count(a); // The first attack roll missed: no weaponDamage call.
  count(a);
  assert.deepEqual(swing(a, t, [3]).map((p) => p.source), ["Club"]);
}
// Initiative lost, or attacker already beyond its opening turn: no rider.
for (const [own, opponent] of [[1, 1], [2, 0]]) {
  const a = attacker(), t = target();
  a.turns_started = own; t.turns_started = opponent;
  count(a);
  assert.deepEqual(swing(a, t, [2]).map((p) => p.source), ["Club"]);
}
// Critical hits double both the printed 2d6 rider and the weapon die.
{
  const a = attacker(), t = target();
  count(a);
  const parts = swing(a, t, [2, 3, 4, 5, 6, 1], true);
  assert.deepEqual(parts[1].rolls, [4, 5, 6, 1]);
}
// Off-turn weapon attempts must count toward the same first-attack entitlement.
{
  const a = attacker(), t = target();
  count(a, true);
  assert.equal(a.feature_use_counts.weapon_attack_attempts, 1);
  count(a);
  assert.deepEqual(swing(a, t, [2]).map((p) => p.source), ["Club"]);
}
// A fresh fight has fresh counters, independent of previous encounters.
{
  const a = attacker(), t = target();
  assert.deepEqual(a.feature_use_counts, {});
  count(a);
  assert.equal(swing(a, t, [2, 3, 4]).length, 2);
}
console.log("2014 first-initiative opening hit damage browser regressions passed.");
