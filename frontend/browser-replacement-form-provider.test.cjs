"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

window.IRON_PIT_ACTION_ECONOMY = { available: (state, cost) => cost === "action" ? state.action_available : cost === "bonus_action" && state.bonus_action_available };
window.IRON_PIT_BROWSER_RESOURCES = {
  available: (state, id, cost = 1) => (state.resources?.[id] || 0) >= cost,
  spend: (state, id, cost = 1) => {
    if ((state.resources?.[id] || 0) < cost) throw new Error("resource unavailable");
    state.resources[id] -= cost;
    return state.resources[id];
  },
};
window.IRON_PIT_BROWSER_SPELL_POLICY = {
  chooseById: (_member, _setup, _turnKey, id) => ({ action: { id, name: "Faerie Fire" }, slotLevel: 1, targetIds: ["monster-1"] }),
};
window.IRON_PIT_BROWSER_SPELL_RESOLUTION = {
  resolve: (sequence) => ({ events: [{ event_type: "feature", feature_id: "faerie-fire" }], sequence: sequence + 1 }),
};
window.IRON_PIT_BROWSER_REPLACEMENT_FORM_COMPILER = {
  compile: (original, form) => ({ ...original, id: original.id + "--form-" + form.id, max_hp: form.max_hp }),
};
window.IRON_PIT_BROWSER_REPLACEMENT_FORMS = {
  enter: (state, action, active) => {
    state.resources[action.resourceId] -= action.resourceCost || 1;
    state.template = active;
    state.replacement_form = { source_id: action.id };
    return { resource_remaining: state.resources[action.resourceId] };
  },
};
window.IRON_PIT_BROWSER_MONSTERS_2014 = { "2014-wolf": { id: "2014-wolf", name: "Wolf", kind: "monster", max_hp: 11 } };
window.IRON_PIT_BROWSER_MONSTERS = { "srd-wolf": { id: "srd-wolf", name: "Wolf", kind: "monster", max_hp: 11 } };

load("browser-resource-conversion.js");
load("browser-main-action-profiles.js");
load("browser-main-action-selection.js");
load("browser-replacement-form-provider.js");

const S = window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION;
const actor = {
  combatant_id: "hero-thalen", side: "heroes",
  state: {
    action_available: true, replacement_form: null, concentration: null, resources: { "wild-shape": 2 },
    template: {
      id: "thalen-greenbough-2014-l2", name: "Thalen Greenbough", kind: "character", ruleset: "2014",
      replacement_form_actions: [{
        id: "wild-shape", name: "Wild Shape", actionCost: "action", formTemplateId: "2014-wolf",
        resourceId: "wild-shape", resourceCost: 1, voluntaryRevertAction: "bonus_action",
        retainSpellcasting: false, setupSpellId: "faerie-fire",
      }],
    },
  },
};
const target = { combatant_id: "monster-1", side: "monsters", state: { template: { ruleset: "2014" } } };
const ctx = { sequence: 4, round: 1, turnKey: "1:hero-thalen", member: actor, setup: { heroes: [actor], monsters: [target] } };

{
  const candidates = S.discoverCandidates("normalPreMove", ctx);
  assert.equal(candidates.length, 1);
  assert.equal(candidates[0].providerId, "replacement-form-setup");
  assert.equal(candidates[0].payload.kind, "setup-spell");
  const resolved = S.resolveCandidate("normalPreMove", candidates[0], ctx);
  assert.equal(resolved.events[0].feature_id, "faerie-fire");
}

{
  actor.state.concentration = { effect_id: "faerie-fire" };
  const candidates = S.discoverCandidates("normalPreMove", ctx);
  assert.equal(candidates[0].payload.kind, "transform");
  const resolved = S.resolveCandidate("normalPreMove", candidates[0], ctx);
  assert.equal(resolved.events[0].feature_id, "wild-shape");
  assert.equal(actor.state.template.id, "thalen-greenbough-2014-l2--form-2014-wolf");
}

console.log("Browser replacement-form Main Action provider parity passed.");

{
  const druid2024 = {
    combatant_id: "hero-thalen-2024", side: "heroes",
    state: {
      action_available: false, bonus_action_available: true, replacement_form: null,
      concentration: null, resources: { "wild-shape": 2 },
      template: {
        id: "thalen-greenbough-l2", name: "Thalen Greenbough", kind: "character", ruleset: "2024",
        replacement_form_actions: [{
          id: "wild-shape", name: "Wild Shape", actionCost: "bonus_action", formTemplateId: "srd-wolf",
          resourceId: "wild-shape", resourceCost: 1, voluntaryRevertAction: "bonus_action",
          hpMode: "retain_owner", temporaryHpOnEnter: 2, retainCreatureType: true,
          replaceExistingForm: true,
        }],
      },
    },
  };
  const ctx2024 = {
    sequence: 8, round: 1, turnKey: "1:hero-thalen-2024", member: druid2024,
    setup: { heroes: [druid2024], monsters: [target] },
  };
  const candidates = S.discoverCandidates("normalPreMove", ctx2024);
  assert.equal(candidates.length, 1);
  assert.equal(candidates[0].payload.kind, "transform");

  const original = druid2024.state.template;
  druid2024.state.replacement_form = {
    source_id: "wild-shape",
    original_template: original,
  };
  druid2024.state.template = { ...original, id: original.id + "--form-srd-wolf" };
  druid2024.state.bonus_action_available = true;
  const refreshCandidates = S.discoverCandidates("normalPreMove", ctx2024);
  assert.equal(refreshCandidates.length, 1, "2024 Wild Shape can be used again while transformed");
  assert.equal(refreshCandidates[0].payload.kind, "transform");
}

{
  actor.state.action_available = true;
  const blocked = S.discoverCandidates("normalPreMove", ctx);
  assert.equal(blocked.length, 0, "2014 Wild Shape cannot replace an active form");
}


{
  const druid5 = {
    combatant_id: "hero-thalen-2024-l5", side: "heroes",
    state: {
      action_available: false, bonus_action_available: true, replacement_form: null,
      concentration: null,
      feature_last_turn_keys: {},
      resources: { "wild-shape": 0, "spell-slot-1": 4, "wild-resurgence-slot-restore": 1 },
      template: {
        id: "thalen-greenbough-l5", name: "Thalen Greenbough", kind: "character", ruleset: "2024",
        resources: { "wild-shape": 2, "spell-slot-1": 4, "wild-resurgence-slot-restore": 1 },
        resource_conversion_actions: [{
          id: "wild-resurgence-regain-wild-shape-slot-1",
          name: "Wild Resurgence (Spend Level 1 Slot)",
          actionCost: "none",
          sourceResourceId: "spell-slot-1",
          sourceCost: 1,
          additionalSourceCosts: {},
          targetResourceId: "wild-shape",
          targetGain: 1,
          targetAllowsOverflow: false,
          requiresTargetEmpty: true,
          oncePerTurn: true,
          oncePerTurnGroup: "wild-resurgence-regain-wild-shape",
          automation: "manual",
          priority: 99,
        }],
        replacement_form_actions: [{
          id: "wild-shape", name: "Wild Shape", actionCost: "bonus_action", formTemplateId: "srd-wolf",
          resourceId: "wild-shape", resourceCost: 1, voluntaryRevertAction: "bonus_action",
          hpMode: "retain_owner", temporaryHpOnEnter: 5, retainCreatureType: true,
          replaceExistingForm: true,
        }],
      },
    },
  };
  const ctx5 = {
    sequence: 12, round: 2, turnKey: "2:hero-thalen-2024-l5", member: druid5,
    setup: { heroes: [druid5], monsters: [target] },
  };
  const candidates = S.discoverCandidates("normalPreMove", ctx5);
  assert.equal(candidates.length, 1, "Wild Resurgence makes zero-use Wild Shape legally restorable");
  assert.equal(candidates[0].payload.kind, "transform");
  const resolved = S.resolveCandidate("normalPreMove", candidates[0], ctx5);
  assert.deepEqual(resolved.events.map((event) => event.feature_id), [
    "wild-resurgence-regain-wild-shape-slot-1", "wild-shape",
  ]);
  assert.equal(druid5.state.resources["spell-slot-1"], 3);
  assert.equal(druid5.state.resources["wild-shape"], 0, "restored use is immediately spent on Wild Shape");
  assert.equal(
    druid5.state.feature_last_turn_keys["wild-resurgence-regain-wild-shape"],
    ctx5.turnKey,
  );
}

{
  const gate = window.IRON_PIT_BROWSER_REPLACEMENT_FORM_PROVIDER.aiMayStartReplacementForm;
  const source = { aiUsePolicy: "emergency_only", aiEmergencyHpFraction: 1 / 3 };
  const owner = { max_hp: 60 };
  const st = (current_hp, replacement_form = null) => ({ current_hp, replacement_form });
  assert.equal(gate(st(60), source, owner), false, "Caster at full HP keeps spells");
  assert.equal(gate(st(21), source, owner), false);
  assert.equal(gate(st(20), source, owner), true, "Emergency buffer unlocked at one-third");
  assert.equal(gate(st(20, { source_id: "wild-shape" }), source, owner), false, "No repeated caster form cycling");
  assert.equal(gate(st(0), source, owner), false, "No Wild Shape when dying");
  assert.equal(gate(st(60), { aiUsePolicy: "tactical" }, owner), true, "Moon/frontline role may shift");
  assert.equal(gate(st(60), { aiUsePolicy: "emergency_only" }, { max_hp: 0 }), false);
}
console.log("Browser Druid emergency source policy checks passed.");
{
  // Regression: a severely injured 2014 caster must transform immediately
  // rather than requesting Faerie Fire first or needing a spell slot.
  const emergency = {
    combatant_id: "emergency-druid", side: "heroes",
    state: {
      action_available: true, current_hp: 6, replacement_form: null,
      concentration: null, resources: { "wild-shape": 1 },
      template: {
        id: "emergency-2014-druid", name: "Emergency Druid",
        kind: "character", ruleset: "2014", max_hp: 18,
        replacement_form_actions: [{
          id: "wild-shape", name: "Wild Shape", actionCost: "action",
          formTemplateId: "2014-wolf", resourceId: "wild-shape",
          resourceCost: 1, setupSpellId: "faerie-fire",
          aiUsePolicy: "emergency_only", aiEmergencyHpFraction: 1 / 3,
        }],
      },
    },
  };
  const emergencyCtx = {
    sequence: 22, round: 2, turnKey: "2:emergency-druid",
    member: emergency, setup: { heroes: [emergency], monsters: [target] },
  };
  const candidate = S.discoverCandidates("normalPreMove", emergencyCtx);
  assert.equal(candidate.length, 1, "Low-HP caster may select a legal form");
  assert.equal(candidate[0].payload.kind, "transform", "Skip optional Faerie Fire");
}
console.log("Emergency form setup bypass regression passed.");
{
  const member = {
    combatant_id: "form-value", side: "heroes",
    state: {
      action_available: true, bonus_action_available: true, current_hp: 8,
      temporary_hp: 0, replacement_form: null, resources: { "wild-shape": 1 },
      template: {
        id: "form-value", name: "Form Value", ruleset: "2024", max_hp: 30,
        replacement_form_actions: [{
          id: "wild-shape", aiUsePolicy: "emergency_only",
          aiEmergencyHpFraction: 1 / 3, actionCost: "bonus_action",
          resourceId: "wild-shape", resourceCost: 1, hpMode: "retain_owner",
          temporaryHpOnEnter: 8,
        }],
      },
    },
  };
  const gate = window.IRON_PIT_BROWSER_REPLACEMENT_FORM_PROVIDER;
  const heal = { id: "healing", actionCost: "bonus_action", maxTargets: 1,
    diceCount: 1, diceSize: 4, healingBonus: 0 };
  assert.equal(gate.preferFormOverSelfHealing(member, heal, "1:form-value"), true);
  assert.equal(gate.preferFormOverSelfHealing(member,
    { ...heal, diceCount: 5, diceSize: 8 }, "1:form-value"), false);
  assert.equal(gate.preferFormOverSelfHealing(member,
    { ...heal, actionCost: "action" }, "1:form-value"), false);
  member.state.temporary_hp = 8;
  assert.equal(gate.aiMayStartReplacementForm(member.state,
    member.state.template.replacement_form_actions[0], member.state.template), false);
  assert.equal(gate.preferFormOverSelfHealing(member, heal, "1:form-value"), false);
}
console.log("Emergency form-versus-healing value parity passed.");
{
  const member = {
    combatant_id: "caster-opportunity", side: "heroes",
    state: {
      current_hp: 8, temporary_hp: 0, action_available: true,
      bonus_action_available: true, replacement_form: null,
      resources: { "wild-shape": 2 },
      template: {
        id: "caster-opportunity", name: "Caster", ruleset: "2024", max_hp: 30,
        replacement_form_actions: [{
          id: "wild-shape", name: "Wild Shape", aiUsePolicy: "emergency_only",
          aiEmergencyHpFraction: 1 / 3, actionCost: "bonus_action",
          formTemplateId: "srd-wolf", resourceId: "wild-shape",
          hpMode: "retain_owner", temporaryHpOnEnter: 8,
        }],
      },
    },
  };
  const setup = { heroes: [member], monsters: [target] };
  const form = member.state.template.replacement_form_actions[0];
  const chooser = window.IRON_PIT_BROWSER_REPLACEMENT_FORM_PROVIDER;
  const spell = { action: { id: "offense", actionCost: "action" }, expectedDamage: 20 };
  window.IRON_PIT_BROWSER_SPELL_OFFENSE = { choose: () => ({ kind: "save", choice: spell }) };
  assert.equal(chooser.deferEmergencyFormForSpell(member, setup, form, "1:caster-opportunity"), true);
  assert.equal(chooser.preferFormOverSelfHealing(member, {
    id: "heal", actionCost: "bonus_action", diceCount: 1, diceSize: 4,
  }, "1:caster-opportunity", setup), false, "No self-heal deferral when form loses to offense");
  let picks = S.discoverCandidates("normalPreMove", {
    sequence: 90, round: 1, member, setup, turnKey: "1:caster-opportunity",
  });
  assert.equal(picks.length, 0, "The emergency form must not starve better legal spell offense");

  member.state.current_hp = 2;
  assert.equal(chooser.deferEmergencyFormForSpell(member, setup, form, "1:caster-opportunity"), false);
  picks = S.discoverCandidates("normalPreMove", {
    sequence: 91, round: 1, member, setup, turnKey: "1:caster-opportunity",
  });
  assert.equal(picks.length, 1, "At critical HP the form gets the survival priority");
  member.state.current_hp = 8;
  form.retainedSpellActionIds = ["offense"];
  assert.equal(chooser.deferEmergencyFormForSpell(member, setup, form, "1:caster-opportunity"), false,
    "No opportunity loss when the spell survives transformation");
  spell.action.actionCost = "bonus_action";
  form.retainedSpellActionIds = [];
  assert.equal(chooser.deferEmergencyFormForSpell(member, setup, form, "1:caster-opportunity"), true,
    "Same bonus-action slot conflicts regardless of retained casting");
  delete window.IRON_PIT_BROWSER_SPELL_OFFENSE;
}
console.log("Emergency form versus spell offense opportunity tests passed.");
