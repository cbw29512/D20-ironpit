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
    template: original, current_hp: 18, temporary_hp: 0, replacement_form: null,
    action_available: true, bonus_action_available: true, reaction_available: true,
    turn_terminated: false, is_dead: false, is_unconscious: false,
    resources: { "wild-shape": 2 }, concentration: { effect_id: "faerie-fire" },
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
  assert.equal(target.concentration.effect_id, "faerie-fire", "Wild Shape must preserve concentration");

  const first = window.IRON_PIT_BROWSER_REPLACEMENT_FORMS.applyDamage(target, 5);
  assert.deepEqual(first, { excess: 0, reverted: false });
  assert.equal(target.replacement_form.form_hp, 6);

  const second = window.IRON_PIT_BROWSER_REPLACEMENT_FORMS.applyDamage(target, 10);
  assert.deepEqual(second, { excess: 4, reverted: true });
  assert.equal(target.replacement_form, null);
  assert.equal(target.template.id, "thalen-l2");
  assert.equal(target.concentration.effect_id, "faerie-fire", "reversion must preserve concentration");
}

{
  window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS = { endDamageSensitive: () => {} };
  window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
  window.IRON_PIT_BROWSER_ZERO_HP_REPLACEMENT = { consumeZero: () => false };
  window.IRON_PIT_BROWSER_STATE = { effectiveMaxHp: (s) => s.template.max_hp };
  const target = state();
  target.concentration = null;
  const active = { id: "thalen-l2--form-2014-wolf", name: "Thalen", kind: "character", max_hp: 11, unlimited_resources: [], traits: [] };
  const action = { id: "wild-shape", name: "Wild Shape", actionCost: "action", resourceId: "wild-shape", resourceCost: 1, voluntaryRevertAction: "bonus_action" };
  window.IRON_PIT_BROWSER_REPLACEMENT_FORMS.enter(target, action, active);
  load("browser-zero-hp.js");
  const outcome = window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(target, 15, false, []);
  assert.equal(outcome, "damaged");
  assert.equal(target.replacement_form, null);
  assert.equal(target.template.id, "thalen-l2");
  assert.equal(target.current_hp, 14, "excess damage after form HP must carry into original HP");
}

console.log("Browser replacement form lifecycle parity passed.");