"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

window.IRON_PIT_ACTION_ECONOMY = { available: (state, cost) => cost === "action" ? state.action_available : cost === "bonus_action" && state.bonus_action_available };
window.IRON_PIT_BROWSER_RESOURCES = { available: () => true };
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
  enter: (state, action, active) => { state.template = active; state.replacement_form = { source_id: action.id }; return { resource_remaining: 1 }; },
};
window.IRON_PIT_BROWSER_MONSTERS_2014 = { "2014-wolf": { id: "2014-wolf", name: "Wolf", kind: "monster", max_hp: 11 } };
window.IRON_PIT_BROWSER_MONSTERS = { "srd-wolf": { id: "srd-wolf", name: "Wolf", kind: "monster", max_hp: 11 } };

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
}


{
  const original = druid2024.state.template;
  druid2024.state.replacement_form = {
    source_id: "wild-shape",
    original_template: original,
  };
  druid2024.state.template = { ...original, id: original.id + "--form-srd-wolf" };
  druid2024.state.bonus_action_available = true;
  const candidates = S.discoverCandidates("normalPreMove", ctx2024);
  assert.equal(candidates.length, 1, "2024 Wild Shape can be used again while transformed");
  assert.equal(candidates[0].payload.kind, "transform");
}

{
  actor.state.action_available = true;
  const blocked = S.discoverCandidates("normalPreMove", ctx);
  assert.equal(blocked.length, 0, "2014 Wild Shape cannot replace an active form");
}
