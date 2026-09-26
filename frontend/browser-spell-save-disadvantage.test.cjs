"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"));

window.IRON_PIT_BROWSER_ROLLS = {
  modeFromSources: (advantage, disadvantage) => {
    if (Boolean(advantage) === Boolean(disadvantage)) return "normal";
    return advantage ? "advantage" : "disadvantage";
  },
  d20: () => ({ natural: 10, total: 10, mode: "normal", rolls: [10], modifier: 0 }),
};
window.IRON_PIT_BROWSER_BARBARIAN2 = { dangerSenseAdvantage: () => 0 };
window.IRON_PIT_BROWSER_DODGE = { dexSaveAdvantageSources: () => 0 };
window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS = {
  saveAdvantage: () => 0,
  saveDisadvantage: () => 0,
  consumeSavingThrowModifiers: () => {},
};
window.IRON_PIT_BROWSER_MODIFIERS = {
  savingThrowFlat: () => 0,
  applyD20Bonus: (_state, _kind, roll) => roll,
};
window.IRON_PIT_BROWSER_EXHAUSTION = { saveDisadvantage: () => 0 };
window.IRON_PIT_BROWSER_CONDITION_RULES = { autoFailStrDex: () => false };

load("browser-resources.js");
load("browser-spell-save-disadvantage.js");
load("browser-saving-throws.js");

const caster = {
  template: {
    name: "Nyra Emberveil",
    unlimited_resources: [],
    spellSaveDisadvantageOptions: [{
      id: "heightened-spell",
      name: "Heightened Spell",
      resourceId: "sorcery-points",
      resourceCost: 3,
      targetPolicy: "first-target",
      priority: 100,
    }],
  },
  resources: { "sorcery-points": 3 },
};

const option = window.IRON_PIT_BROWSER_SPELL_SAVE_DISADVANTAGE.choose(caster);
assert.equal(option.id, "heightened-spell");
assert.equal(window.IRON_PIT_BROWSER_SPELL_SAVE_DISADVANTAGE.spend(caster, option), 0);
assert.equal(caster.resources["sorcery-points"], 0);
assert.equal(window.IRON_PIT_BROWSER_SPELL_SAVE_DISADVANTAGE.choose(caster), null);

const target = {
  template: { name: "Target", saving_throw_bonuses: { dexterity: 0 } },
  active_effect_ids: [],
  active_d20_bonus_dice: [],
};
assert.equal(
  window.IRON_PIT_BROWSER_SAVING_THROWS.saveMode(
    target,
    "dexterity",
    { disadvantageSources: ["Heightened Spell"] },
  ),
  "disadvantage",
);

console.log("Browser resource-backed spell save Disadvantage regressions passed.");
