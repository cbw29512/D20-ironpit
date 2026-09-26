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

function queuedDice(values) {
  const queue = [...values];
  return {
    roll: (sides) => {
      const value = queue.shift();
      assert.ok(value >= 1 && value <= sides);
      return value;
    },
    rollMany: (count, sides) => Array.from({ length: count }, () => window.IRON_PIT_DICE.roll(sides)),
  };
}

window.IRON_PIT_BROWSER_CONDITION_RULES = { autoFailStrDex: () => false };
window.IRON_PIT_BROWSER_BARBARIAN2 = { dangerSenseAdvantage: () => 0 };
window.IRON_PIT_BROWSER_DODGE = { dexSaveAdvantageSources: () => 0 };
window.IRON_PIT_BROWSER_EXHAUSTION = { saveDisadvantage: () => 0, d20Modifier: () => 0 };
load("browser-opening-modifiers.js");
load("browser-modifiers.js");
load("browser-defensive-modifier-rules.js");
load("browser-rolls.js");
load("browser-saving-throws.js");
load("browser-saves.js");
load("browser-spell-resolution.js");

const template = {
  id: "satyr",
  name: "Satyr",
  saving_throw_bonuses: { wisdom: 0 },
  saving_throw_advantage_grants: [{
    source_id: "magic-resistance",
    source_name: "Magic Resistance",
    abilities: ["wisdom"],
    requires_magical_effect: true,
  }],
};
const state = {
  template,
  active_effect_ids: [],
  active_modifiers: window.IRON_PIT_BROWSER_OPENING_MODIFIERS.build(template),
};

window.IRON_PIT_DICE = queuedDice([2, 17]);
const magical = window.IRON_PIT_BROWSER_SAVES.resolveSavingThrow(
  state, "wisdom", 99, { magicalEffect: true },
);
assert.equal(magical.roll.mode, "advantage");
assert.deepEqual(magical.roll.rolls, [2, 17]);
assert.deepEqual(
  window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS.saveAdvantageSourceNames(
    state, "wisdom", { magicalEffect: true },
  ),
  ["Magic Resistance"],
);

window.IRON_PIT_DICE = queuedDice([10]);
const nonmagical = window.IRON_PIT_BROWSER_SAVES.resolveSavingThrow(
  state, "wisdom", 99, { magicalEffect: false },
);
assert.equal(nonmagical.roll.mode, "normal");
assert.deepEqual(nonmagical.roll.rolls, [10]);

const converted = window.IRON_PIT_BROWSER_SPELL_RESOLUTION.saveAction({
  slotLevel: 0,
  action: {
    id: "test-spell", name: "Test Spell", level: 0, range: 60,
    saveAbility: "wisdom", dc: 12, damageDiceCount: 0,
    damageDiceSize: 6, damageBonus: 0, damageType: null,
    successDamage: "none", animation: "spell-save",
  },
});
assert.equal(converted.magicalEffect, true);
assert.deepEqual(converted.effectTags, []);

const poisonTemplate = {
  id: "dwarf-test",
  name: "Dwarf Test",
  saving_throw_bonuses: { constitution: 0 },
  saving_throw_advantage_grants: [{
    source_id: "dwarven-resilience",
    source_name: "Dwarven Resilience",
    abilities: ["constitution"],
    required_effect_tags: ["poison"],
  }],
};
const poisonState = {
  template: poisonTemplate,
  active_effect_ids: [],
  active_modifiers: window.IRON_PIT_BROWSER_OPENING_MODIFIERS.build(poisonTemplate),
};

window.IRON_PIT_DICE = queuedDice([3, 18]);
const poison = window.IRON_PIT_BROWSER_SAVES.resolveSavingThrow(
  poisonState, "constitution", 99, { effectTags: ["poison"] },
);
assert.equal(poison.roll.mode, "advantage");
assert.deepEqual(poison.roll.rolls, [3, 18]);
assert.deepEqual(
  window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS.saveAdvantageSourceNames(
    poisonState, "constitution", { effectTags: ["poison"] },
  ),
  ["Dwarven Resilience"],
);

window.IRON_PIT_DICE = queuedDice([11]);
const ordinaryPoisonState = {
  template: poisonTemplate,
  active_effect_ids: [],
  active_modifiers: window.IRON_PIT_BROWSER_OPENING_MODIFIERS.build(poisonTemplate),
};
const ordinarySave = window.IRON_PIT_BROWSER_SAVES.resolveSavingThrow(
  ordinaryPoisonState, "constitution", 99, {},
);
assert.equal(ordinarySave.roll.mode, "normal");
assert.deepEqual(ordinarySave.roll.rolls, [11]);

console.log("Browser contextual saving-throw Advantage regressions passed.");
