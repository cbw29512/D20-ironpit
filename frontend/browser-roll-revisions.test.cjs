"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
const queueDice = (values) => {
  const queue = [...values];
  window.IRON_PIT_DICE = {
    roll: (sides) => { const value = queue.shift(); assert.ok(value >= 1 && value <= sides); return value; },
    rollMany: (count, sides) => Array.from({ length: count }, () => window.IRON_PIT_DICE.roll(sides)),
  };
};

load("browser-heroic-inspiration.js");
{
  const state = { template: { heroic_warrior: true }, heroic_inspiration: true };
  queueDice([8]);
  const result = window.IRON_PIT_BROWSER_HEROIC_INSPIRATION.rerollFailedAttack(
    state, { notation: "1d20", rolls: [5], modifier: 9, selected_roll: 5, mode: "normal", total: 14 }, 17,
  );
  assert.equal(result.roll.revisions.length, 1);
  assert.deepEqual(result.roll.revisions[0].original_rolls, [5]);
  assert.deepEqual(result.roll.revisions[0].replacement_rolls, [8]);
  assert.equal(result.roll.revisions[0].kind, "die_replacement");
  assert.equal(result.roll.revisions[0].accepted, "replacement");
}

window.IRON_PIT_BROWSER_RAGE = { damageBonus: () => 0 };
window.IRON_PIT_BROWSER_SNEAK_ATTACK = { bonusDamage: () => null };
window.IRON_PIT_BROWSER_BARBARIAN3 = { bonusDamage: () => null };
load("browser-rolls.js");
{
  queueDice([1, 2, 6, 6]);
  const attacker = { template: { traits: ["savage-attacker"] }, feature_last_turn_keys: {} };
  const attack = { name: "Greatsword", kind: "melee", diceCount: 2, diceSize: 6, damageBonus: 3, damageType: "slashing" };
  const result = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(attacker, attack, false, "normal", "1:hero");
  const revision = result.components[0].revisions[0];
  assert.deepEqual(revision.original_rolls, [1, 2]);
  assert.deepEqual(revision.replacement_rolls, [6, 6]);
  assert.equal(revision.kind, "roll_twice_choose");
  assert.equal(revision.accepted, "replacement");
  assert.deepEqual(result.components[0].rolls, [6, 6]);
}

window.IRON_PIT_BROWSER_ROLLS = {
  modeFromSources: () => "normal",
  d20: () => ({ notation: "1d20", rolls: [2], modifier: 0, selected_roll: 2, mode: "normal", total: 2 }),
  bloodiedSaveAdvantage: () => 0,
};
window.IRON_PIT_BROWSER_MODIFIERS = { applyD20Bonus: (_state, _kind, roll) => roll };
window.IRON_PIT_BROWSER_BARBARIAN2 = { dangerSenseAdvantage: () => 0 };
window.IRON_PIT_BROWSER_CONDITION_RULES = { autoFailStrDex: () => false };
window.IRON_PIT_BROWSER_INDOMITABLE = {
  use: () => ({ notation: "1d20 [Indomitable +9]", rolls: [10], modifier: 9, selected_roll: 10, mode: "normal", total: 19 }),
};
load("browser-saves.js");
{
  const state = { template: { name: "Karnok", saving_throw_bonuses: { wisdom: 0 } }, active_effect_ids: [] };
  const result = window.IRON_PIT_BROWSER_SAVES.resolveSavingThrow(state, "wisdom", 15);
  assert.equal(result.succeeded, true);
  const revision = result.roll.revisions[0];
  assert.equal(revision.source_effect_id, "indomitable");
  assert.equal(revision.kind, "full_reroll");
  assert.deepEqual(revision.original_rolls, [2]);
  assert.deepEqual(revision.replacement_rolls, [10]);
  assert.equal(revision.original_total, 2);
  assert.equal(revision.replacement_total, 19);
}

console.log("Browser roll-revision producers preserve original and accepted candidates.");