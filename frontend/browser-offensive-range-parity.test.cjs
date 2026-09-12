"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

load("browser-resources.js");
load("browser-spellcasting.js");
window.IRON_PIT_ACTION_ECONOMY = { available: () => true };
window.IRON_PIT_BROWSER_STATE = { sizeAtMost: () => true };
window.IRON_PIT_BROWSER_CONDITION_RULES = { has: () => false };
window.IRON_PIT_BROWSER_TIMED = { affectedByAction: () => false };
load("browser-offensive-ranges.js");

const ranges = window.IRON_PIT_BROWSER_OFFENSIVE_RANGES;
const spellcasting = window.IRON_PIT_BROWSER_SPELLCASTING;

function member(template, resources = {}) {
  return {
    combatant_id: "actor",
    state: {
      template: { id: "actor", name: "Actor", resourceDefinitions: {}, ...template },
      resources,
      grapple_sources: [],
      spell_slot_expended_turn_key: null,
    },
  };
}

const target = {
  combatant_id: "target",
  state: { template: { size: "medium" }, grapple_sources: [], timed_effects: [] },
};

{
  const actor = member({
    attacks: [{ id: "bow", kind: "ranged", normal: 80, long: 320 }],
    spell_attack_actions: [], spell_save_actions: [], automatic_spell_actions: [], saving_throw_actions: [],
  });
  const [profile] = ranges.rangesForTarget(actor, target, "1:actor");
  assert.equal(profile.maxRange, 320);
  assert.equal(profile.preferredRange, 80);
  assert.equal(profile.executionRank, 2);
}

{
  const state = member({}, { "spell-slot-1": 1 }).state;
  state.spell_slot_expended_turn_key = "1:actor";
  assert.equal(spellcasting.actionResourceAvailable(
    state, { level: 1, resourceId: null, resourceCost: 1 }, "1:actor",
  ), false);
  state.resources = { "arcane-charge": 1 };
  assert.equal(spellcasting.actionResourceAvailable(
    state, { level: 1, resourceId: "arcane-charge", resourceCost: 1 }, "1:actor",
  ), true);
}

{
  const actor = member({
    attacks: [], spell_attack_actions: [], spell_save_actions: [], saving_throw_actions: [],
    automatic_spell_actions: [{ id: "bolt", actionCost: "action", level: 1,
      resourceId: "arcane-charge", resourceCost: 1, range: 60 }],
  }, { "arcane-charge": 1 });
  actor.state.spell_slot_expended_turn_key = "1:actor";
  const [profile] = ranges.rangesForTarget(actor, target, "1:actor");
  assert.equal(profile.family, "spell");
  assert.equal(profile.maxRange, 60);
}

{
  assert.equal(ranges.effectiveActionRange({
    id: "cone", range: 0, area: { shape: "cone", origin: "self", lengthFt: 30 },
  }), 30);
  assert.equal(ranges.effectiveActionRange({
    id: "blast", range: 60, area: { shape: "radius", origin: "point", radiusFt: 20 },
  }), 80);
}

console.log("Browser offensive range parity regressions passed.");
