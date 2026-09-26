"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

window.IRON_PIT_BROWSER_CONDITION_RULES = { incapacitated: () => false };
window.IRON_PIT_BROWSER_TIMED = { suppressesAction: () => false, suppressesBonusAction: () => false, suppressesReactions: () => false };
load("browser-action-economy.js");
load("browser-resources.js");
load("browser-replacement-forms.js");

function state() {
  const original = {
    id: "thalen-l2", name: "Thalen", kind: "character", unlimited_resources: [], max_hp: 18,
  };
  return {
    template: original, current_hp: 18, replacement_form: null,
    action_available: true, bonus_action_available: true, reaction_available: true,
    turn_terminated: false, is_dead: false, is_unconscious: false,
    resources: { "wild-shape": 2 },
  };
}

{
  const target = state();
  const active = { id: "thalen-l2--form-2014-wolf", name: "Thalen", kind: "character", max_hp: 11, unlimited_resources: [] };
  const action = { id: "wild-shape", name: "Wild Shape", actionCost: "action", resourceId: "wild-shape", resourceCost: 1, voluntaryRevertAction: "bonus_action" };
  const entered = window.IRON_PIT_BROWSER_REPLACEMENT_FORMS.enter(target, action, active);
  assert.equal(entered.resource_remaining, 1);
  assert.equal(target.template.id, active.id);
  assert.equal(target.replacement_form.form_hp, 11);
  assert.equal(target.action_available, false);
  assert.equal(target.resources["wild-shape"], 1);

  const first = window.IRON_PIT_BROWSER_REPLACEMENT_FORMS.applyDamage(target, 5);
  assert.deepEqual(first, { excess: 0, reverted: false });
  assert.equal(target.replacement_form.form_hp, 6);

  const second = window.IRON_PIT_BROWSER_REPLACEMENT_FORMS.applyDamage(target, 10);
  assert.deepEqual(second, { excess: 4, reverted: true });
  assert.equal(target.replacement_form, null);
  assert.equal(target.template.id, "thalen-l2");
}

console.log("Browser replacement form lifecycle parity passed.");