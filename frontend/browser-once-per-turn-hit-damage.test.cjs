"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(`frontend/${name}`, "utf8"), { filename: name });

window.IRON_PIT_DICE = {
  rolls: [],
  roll(sides) {
    if (!this.rolls.length) throw new Error(`No queued d${sides} roll`);
    return this.rolls.shift();
  },
  rollMany(count, sides) {
    return Array.from({ length: count }, () => this.roll(sides));
  },
};

load("browser-once-per-turn-hit-damage.js");
load("browser-rolls.js");

const attacker = {
  template: {
    max_hp: 20,
    traits: [],
    once_per_turn_weapon_hit_damage_rider: {
      source_id: "test-rider",
      source_name: "Test Rider",
      dice_count: 1,
      dice_size: 8,
      damage_type: "radiant",
    },
  },
  current_hp: 20,
  feature_last_turn_keys: {},
};

const attack = {
  name: "Warhammer",
  kind: "melee",
  diceCount: 1,
  diceSize: 8,
  damageBonus: 1,
  damageType: "bludgeoning",
  onHitDamage: [],
};

window.IRON_PIT_DICE.rolls = [4, 6];
let result = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(attacker, attack, false, "normal", "1:attacker");
assert.deepEqual(result.components.map((part) => part.source), ["Warhammer", "Test Rider"]);
assert.equal(result.roll.total, 11);

window.IRON_PIT_DICE.rolls = [5];
result = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(attacker, attack, false, "normal", "1:attacker");
assert.deepEqual(result.components.map((part) => part.source), ["Warhammer"]);
assert.equal(result.roll.total, 6);

window.IRON_PIT_DICE.rolls = [4, 5, 6, 7];
result = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(attacker, attack, true, "normal", "2:attacker");
assert.deepEqual(result.components.map((part) => part.source), ["Warhammer", "Test Rider"]);
assert.deepEqual(result.components[1].rolls, [6, 7]);

console.log("Browser once-per-turn weapon-hit damage rider regressions passed.");

const conditionalAttacker = {
  template: {
    max_hp: 20,
    traits: [],
    once_per_turn_weapon_hit_damage_rider: {
      source_id: "conditional-rider",
      source_name: "Conditional Rider",
      dice_count: 1,
      dice_size: 8,
      damage_type: "slashing",
      requires_target_below_max_hp: true,
    },
  },
  current_hp: 20,
  feature_last_turn_keys: {},
};
const conditionalTarget = { template: { max_hp: 30 }, current_hp: 30, max_hp_bonus: 0 };
window.IRON_PIT_DICE.rolls = [4];
result = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(
  conditionalAttacker, attack, false, "normal", "1:conditional", null, conditionalTarget,
);
assert.deepEqual(result.components.map((part) => part.source), ["Warhammer"]);
assert.equal(conditionalAttacker.feature_last_turn_keys["conditional-rider"], undefined);

conditionalTarget.current_hp = 29;
window.IRON_PIT_DICE.rolls = [4, 6];
result = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(
  conditionalAttacker, attack, false, "normal", "1:conditional", null, conditionalTarget,
);
assert.deepEqual(result.components.map((part) => part.source), ["Warhammer", "Conditional Rider"]);
