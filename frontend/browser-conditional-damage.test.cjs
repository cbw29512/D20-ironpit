"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-rolls.js"), "utf8"));

function fixedDice(values) {
  const queue = [...values];
  window.IRON_PIT_DICE = {
    roll: () => queue.shift(),
    rollMany: (count) => Array.from({ length: count }, () => queue.shift()),
  };
}

const state = (hp, maxHp = 10) => ({
  current_hp: hp,
  template: { max_hp: maxHp, traits: [] },
  feature_last_turn_keys: {},
  grapple_sources: [],
});
const attack = (trigger) => ({
  id: "test-beak", name: "Beak", kind: "melee", diceCount: 1, diceSize: 4,
  damageBonus: 2, damageType: "piercing",
  conditionalDamage: trigger ? {
    trigger, mode: "replace_weapon", diceCount: 1, diceSize: 8,
    damageBonus: 2, damageType: "piercing",
  } : null,
});

fixedDice([3]);
let result = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(
  state(10), attack("target_bloodied"), false, "normal", "1:test", null, state(10),
);
assert.equal(result.roll.total, 5);
assert.equal(result.components[0].notation, "1d4+2");

fixedDice([7]);
result = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(
  state(10), attack("target_bloodied"), false, "normal", "1:test", null, state(5),
);
assert.equal(result.roll.total, 9);
assert.equal(result.components[0].notation, "1d8+2");

fixedDice([6]);
result = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(
  state(5), attack("attacker_bloodied"), false, "normal", "1:test", null, state(10),
);
assert.equal(result.roll.total, 8);
assert.equal(result.components[0].notation, "1d8+2");

fixedDice([7, 6]);
result = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(
  state(10), attack("target_bloodied"), true, "normal", "1:test", null, state(5),
);
assert.equal(result.roll.total, 15);
assert.equal(result.components[0].notation, "2d8+2");

const heldBySelf = state(10); heldBySelf.grapple_sources.push({ source_id: "attacker-1" });
fixedDice([7]);
result = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(
  state(10), attack("target_grappled_by_self"), false, "normal", "1:test", null, heldBySelf, false, "attacker-1",
);
assert.equal(result.roll.total, 9);
assert.equal(result.components[0].notation, "1d8+2");

const heldByOther = state(10); heldByOther.grapple_sources.push({ source_id: "other-1" });
fixedDice([4]);
result = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(
  state(10), attack("target_grappled_by_self"), false, "advantage", "1:test", null, heldByOther, false, "attacker-1",
);
assert.equal(result.roll.total, 6);
assert.equal(result.components[0].notation, "1d4+2");

fixedDice([4, 3]);
const legacy = { ...attack(null), conditionalAdvantage: [1, 4] };
result = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(state(10), legacy, false, "advantage", "1:test");
assert.equal(result.roll.total, 9);
assert.deepEqual(result.components.map((item) => item.notation), ["1d4+2", "1d4+0"]);

console.log("Browser conditional damage preserves legacy, Bloodied, and source-aware grapple replacement profiles.");
