"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"));
window.IRON_PIT_BROWSER_CONDITION_RULES = { incapacitated: () => false };
window.IRON_PIT_BROWSER_TIMED = {
  suppressesAction: () => false, suppressesBonusAction: () => false,
  suppressesReactions: () => false,
};
load("browser-action-economy.js");
load("browser-resources.js");
load("browser-replacement-forms.js");

function fight() {
  const original = {
    id: "original-monster", name: "Source creature", kind: "monster",
    max_hp: 24, unlimited_resources: [],
  };
  const state = {
    template: original, current_hp: 24, temporary_hp: 0, replacement_form: null,
    action_available: true, bonus_action_available: true, reaction_available: true,
    is_dead: false, is_unconscious: false, resources: {},
  };
  const form = {
    id: "original-monster--form-new", name: "Transformed",
    kind: "monster", max_hp: 24, unlimited_resources: [],
  };
  return { state, original, form };
}
{
  const { state, original, form } = fight();
  const action = {
    id: "shape", name: "Print Change Shape", actionCost: "action",
    hpMode: "retain_owner", voluntaryRevertAction: "action",
    endsOnDeath: true, endsOnIncapacitated: false,
  };
  window.IRON_PIT_BROWSER_REPLACEMENT_FORMS.enter(state, action, form);
  assert.equal(state.replacement_form.ends_on_death, true);
  state.is_unconscious = true;
  assert.equal(window.IRON_PIT_BROWSER_REPLACEMENT_FORMS.revertIfIncapacitated(state), false);
  assert.equal(state.template.id, form.id);
  state.is_unconscious = false;
  state.current_hp = 0;
  state.is_dead = true;
  assert.equal(window.IRON_PIT_BROWSER_REPLACEMENT_FORMS.revertIfIncapacitated(state), true);
  assert.equal(state.template.id, original.id);
  assert.equal(state.replacement_form, null);
  assert.equal(state.is_dead, true);
  assert.equal(state.current_hp, 0);
}
{
  const { state, original, form } = fight();
  window.IRON_PIT_BROWSER_REPLACEMENT_FORMS.enter(state, {
    id: "old-form", name: "Wild Shape", actionCost: "action",
    endsOnIncapacitated: true,
  }, form);
  assert.equal(state.replacement_form.ends_on_death, false);
  state.is_unconscious = true;
  assert.equal(window.IRON_PIT_BROWSER_REPLACEMENT_FORMS.revertIfIncapacitated(state), true);
  assert.equal(state.template.id, original.id);
}
console.log("Source-specific death-only form lifecycle Python/browser parity passed.");
