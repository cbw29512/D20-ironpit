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

let rolls = [];
window.IRON_PIT_BROWSER_ROLLS = {
  d20: (bonus, mode) => {
    const selected = rolls.shift();
    if (selected == null) throw new Error("No deterministic d20 result remains.");
    return {
      notation: "1d20", rolls: [selected], modifier: bonus, selected_roll: selected,
      mode, total: selected + bonus, revisions: [],
    };
  },
  modeFromSources: (advantage, disadvantage) => (
    advantage && !disadvantage ? "advantage" : disadvantage && !advantage ? "disadvantage" : "normal"
  ),
};
window.IRON_PIT_BROWSER_MODIFIERS = {
  applyD20Bonus: (_state, _kind, roll) => roll,
  savingThrowFlat: () => 0,
};
window.IRON_PIT_BROWSER_BARBARIAN2 = { dangerSenseAdvantage: () => 0 };
window.IRON_PIT_BROWSER_DODGE = { dexSaveAdvantageSources: () => 0 };
window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS = {
  saveAdvantage: () => 0,
  saveDisadvantage: () => 0,
  consumeSavingThrowModifiers: () => [],
};
window.IRON_PIT_BROWSER_EXHAUSTION = { saveDisadvantage: () => 0 };
window.IRON_PIT_BROWSER_CONDITION_RULES = { autoFailStrDex: () => false };

load("browser-indomitable.js");
load("browser-saves.js");

{
  const monk = {
    template: {
      name: "Kael Stillwater",
      saving_throw_bonuses: { constitution: 7 },
      failed_save_reroll_source_id: "diamond-soul",
      failed_save_reroll_resource_id: "ki",
    },
    resources: { ki: 14 },
    active_effect_ids: [],
  };
  rolls = [1, 20];
  const result = window.IRON_PIT_BROWSER_SAVES.resolveSavingThrow(monk, "constitution", 20);
  assert.equal(result.succeeded, true);
  assert.equal(result.roll.total, 27);
  assert.equal(result.roll.revisions.at(-1).source_effect_id, "diamond-soul");
  assert.equal(monk.resources.ki, 13);
}

{
  const fighter = {
    template: {
      name: "Karnok Stoneward",
      saving_throw_bonuses: { wisdom: 0 },
      indomitable_reroll: true,
      indomitable_bonus: 0,
    },
    resources: { indomitable: 1 },
    active_effect_ids: [],
  };
  rolls = [2, 15];
  const result = window.IRON_PIT_BROWSER_SAVES.resolveSavingThrow(fighter, "wisdom", 10);
  assert.equal(result.succeeded, true);
  assert.equal(result.roll.revisions.at(-1).source_effect_id, "indomitable");
  assert.equal(fighter.resources.indomitable, 0);
}

console.log("Generic failed-save reroll supports Diamond Soul Ki and legacy Indomitable.");
