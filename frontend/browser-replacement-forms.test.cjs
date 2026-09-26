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

{
  const target = state();
  target.template = {
    ...target.template,
    id: "thalen-greenbough-2014-l2", name: "Thalen Greenbough", archetype: "Druid",
    level: 2, ruleset: "2014", saving_throw_bonuses: { intelligence: 3, wisdom: 5 },
    skill_bonuses: { perception: 5 }, resources: { "wild-shape": 2 },
    spell_attack_actions: [{ id: "produce-flame" }], spell_save_actions: [{ id: "poison-spray" }],
    defensive_spell_actions: [{ id: "longstrider" }], healingActions: [{ id: "healing-word" }], source: "2014 Druid",
  };
  window.IRON_PIT_BROWSER_MONSTERS_2014 = {
    "2014-wolf": {
      id: "2014-wolf", name: "Wolf", kind: "monster", ruleset: "2014", max_hp: 11,
      armor_class: 13, speed_ft: 40, size: "medium", saving_throw_bonuses: {},
      skill_bonuses: { perception: 3 }, resources: {}, attacks: [{ id: "2014-wolf-bite" }],
      primary_attack_id: "2014-wolf-bite", source: "2014 Wolf",
    },
  };
  const action = {
    id: "wild-shape", name: "Wild Shape", actionCost: "action", formTemplateId: "2014-wolf",
    resourceId: "wild-shape", resourceCost: 1, voluntaryRevertAction: "bonus_action", retainSpellcasting: false,
  };
  const result = window.IRON_PIT_BROWSER_REPLACEMENT_FORMS.resolveAction(target, action);
  assert.equal(result.resource_remaining, 1);
  assert.equal(target.template.id, "thalen-greenbough-2014-l2--form-2014-wolf");
  assert.equal(target.template.armor_class, 13);
  assert.equal(target.template.speed_ft, 40);
  assert.equal(target.template.primary_attack_id, "2014-wolf-bite");
  assert.deepEqual(target.template.spell_attack_actions, []);
  assert.equal(target.concentration.effect_id, "faerie-fire");
}


{
  const owner = {
    id: "thalen-greenbough-2014-l18", name: "Thalen Greenbough", archetype: "Druid",
    level: 18, kind: "character", ruleset: "2014", resources: { "wild-shape": 2 },
    unlimited_resources: [], saving_throw_bonuses: {}, skill_bonuses: {}, source: "2014 Druid",
    spell_attack_actions: [{ id: "produce-flame" }],
    spell_save_actions: [{ id: "poison-spray" }, { id: "faerie-fire" }],
    persistent_spell_attack_actions: [],
    defensive_spell_actions: [{ id: "longstrider" }, { id: "barkskin" }, { id: "freedom-of-movement" }],
    healingActions: [{ id: "healing-word" }, { id: "cure-wounds" }],
    condition_removal_actions: [{ id: "lesser-restoration" }],
    effect_removal_actions: [{ id: "dispel-magic" }],
  };
  const form = {
    id: "2014-brown-bear", name: "Brown Bear", kind: "monster", ruleset: "2014",
    max_hp: 34, armor_class: 11, speed_ft: 40, size: "large",
    saving_throw_bonuses: {}, skill_bonuses: {}, resources: {}, attacks: [],
    source: "2014 Brown Bear",
  };
  const beastSpellIds = [
    "produce-flame", "poison-spray", "faerie-fire", "healing-word",
    "cure-wounds", "lesser-restoration", "dispel-magic",
  ];
  const active18 = window.IRON_PIT_BROWSER_REPLACEMENT_FORMS.compileActiveTemplate(
    owner, form, true, beastSpellIds,
  );
  const ids18 = [
    ...(active18.spell_attack_actions || []), ...(active18.spell_save_actions || []),
    ...(active18.persistent_spell_attack_actions || []), ...(active18.defensive_spell_actions || []),
    ...(active18.healingActions || []), ...(active18.condition_removal_actions || []),
    ...(active18.effect_removal_actions || []),
  ].map((action) => action.id);
  assert.deepEqual(new Set(ids18), new Set(beastSpellIds));
  assert.ok(!ids18.includes("longstrider"));
  assert.ok(!ids18.includes("barkskin"));
  assert.ok(!ids18.includes("freedom-of-movement"));

  const archdruidIds = [...beastSpellIds, "longstrider", "barkskin", "freedom-of-movement"];
  const active20 = window.IRON_PIT_BROWSER_REPLACEMENT_FORMS.compileActiveTemplate(
    { ...owner, id: "thalen-greenbough-2014-l20", level: 20, unlimited_resources: ["wild-shape"] },
    form, true, archdruidIds,
  );
  const ids20 = [
    ...(active20.spell_attack_actions || []), ...(active20.spell_save_actions || []),
    ...(active20.persistent_spell_attack_actions || []), ...(active20.defensive_spell_actions || []),
    ...(active20.healingActions || []), ...(active20.condition_removal_actions || []),
    ...(active20.effect_removal_actions || []),
  ].map((action) => action.id);
  assert.deepEqual(new Set(ids20), new Set(archdruidIds));
}

console.log("Browser replacement form lifecycle parity passed.");