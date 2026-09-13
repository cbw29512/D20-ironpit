"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

window.IRON_PIT_BROWSER_ATTACK = { adjustedDamage: (_state, amount) => amount, applyDamage: () => null };
window.IRON_PIT_BROWSER_GRAPPLE = { apply: () => [] };
window.IRON_PIT_BROWSER_STATE = { sizeAtMost: () => true };
window.IRON_PIT_BROWSER_BARBARIAN2 = { dangerSenseAdvantage: () => 0 };
window.IRON_PIT_BROWSER_DODGE = { dexSaveAdvantageSources: () => 0 };
window.IRON_PIT_BROWSER_MODIFIERS = { applyD20Bonus: (_state, _kind, roll) => roll };
window.IRON_PIT_ACTION_ECONOMY = { available: () => true, spend: () => {} };
window.IRON_PIT_BROWSER_CONDITION_RULES = { autoFailStrDex: () => false };
load("browser-rolls.js");
load("browser-saves.js");

const V = window.IRON_PIT_BROWSER_SAVES;
function state() {
  return {
    active_effect_ids: [],
    resources: {},
    template: {
      name: "2014 Magic Resistant Monster",
      traits: ["magic-resistance"],
      saving_throw_bonuses: { wisdom: 0, dexterity: 0 },
    },
  };
}
function dice(values) {
  const queue = [...values];
  window.IRON_PIT_DICE = {
    roll: () => queue.shift(),
    rollMany: (count) => Array.from({ length: count }, () => queue.shift()),
  };
}

{
  const target = state(); dice([4, 14]);
  const result = V.resolveSavingThrow(target, "wisdom", 12, { magicalEffect: true });
  assert.equal(result.roll.mode, "advantage");
  assert.deepEqual(result.roll.rolls, [4, 14]);
  assert.equal(result.succeeded, true);
}
{
  const target = state(); dice([4]);
  const result = V.resolveSavingThrow(target, "wisdom", 12, { magicalEffect: false });
  assert.equal(result.roll.mode, "normal");
  assert.deepEqual(result.roll.rolls, [4]);
  assert.equal(result.succeeded, false);
}
{
  const target = state(); target.active_effect_ids.push("restrained"); dice([11]);
  const result = V.resolveSavingThrow(target, "dexterity", 12, { magicalEffect: true });
  assert.equal(result.roll.mode, "normal", "Magic Resistance advantage and Restrained disadvantage must cancel");
}
{
  const target = state(); target.resources["legendary-resistance"] = 2; dice([2, 3]);
  const result = V.resolveSavingThrow(target, "wisdom", 20, { magicalEffect: true });
  assert.equal(result.succeeded, true);
  assert.equal(result.legendaryResistanceUsed, true);
  assert.equal(result.legendaryResistanceRemaining, 1);
}

console.log("2014 browser Magic Resistance and Legendary Resistance save regressions passed.");
