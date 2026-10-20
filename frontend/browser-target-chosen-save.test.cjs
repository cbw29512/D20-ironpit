"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
let dexDisadvantage = false;
window.IRON_PIT_BROWSER_SAVING_THROWS = {
  saveMode: (_state, ability) =>
    dexDisadvantage && ability === "dexterity" ? "disadvantage" : "normal",
};
window.IRON_PIT_BROWSER_ABILITY_SCORE_REDUCTION = {
  abilityModifierDelta: (state, ability) => state.reduction?.[ability] || 0,
};
window.IRON_PIT_BROWSER_MODIFIERS = { savingThrowFlat: () => 0 };
load("browser-target-chosen-save.js");

const state = {
  template: { saving_throw_bonuses: { strength: 2, dexterity: 4 } },
  active_effect_ids: [], reduction: {},
};
const options = ["strength", "dexterity"];
const choose = window.IRON_PIT_BROWSER_TARGET_CHOSEN_SAVE.choose;
assert.equal(choose(state, options, 16), "dexterity");
dexDisadvantage = true;
assert.equal(choose(state, options, 16), "strength");
dexDisadvantage = false;
state.reduction.dexterity = -5;
assert.equal(choose(state, options, 16), "strength");
assert.deepEqual(options, ["strength", "dexterity"], "Choice must not mutate source parameters");
assert.deepEqual(state.template.saving_throw_bonuses, { strength: 2, dexterity: 4 });
assert.throws(() => choose(state, ["strength", "strength"], 16), /distinct/);
console.log("Universal target-selected saving throws use live probability without mutating source cards.");
