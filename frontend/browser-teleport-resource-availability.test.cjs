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
load("browser-action-economy.js");
load("browser-teleport-cancel.js");
load("browser-teleport.js");

const action = {
  id: "misty-step",
  name: "Misty Step",
  level: 2,
  actionCost: "bonus_action",
  range: 30,
  resourceId: "misty-step",
  resourceCost: 1,
  expendsSpellSlot: false,
};
const state = {
  position: { x: 6, y: 6 },
  template: { teleport_actions: [action] },
  resources: { "misty-step": 0 },
  timed_effects: [{ effect_id: "restrained", ground_contact: true, ends_on_teleport: true }],
  grapple_sources: [],
  delayed_resource_refills: [],
  is_dead: false,
  is_unconscious: false,
  turn_terminated: false,
  bonus_action_available: true,
};
const caster = { combatant_id: "cloud-giant", state };
const TP = window.IRON_PIT_BROWSER_TELEPORT;

const activeHold = state.timed_effects[0];
state.timed_effects = [];
assert.equal(TP.choose(caster, {}, "1:cloud-giant"), null,
  "no eligible hold means no Misty Step cast");
state.timed_effects = [activeHold];
assert.equal(TP.choose(caster, {}, "1:cloud-giant"), null,
  "an active hold cannot select an exhausted Misty Step");
state.resources["misty-step"] = 3;
const choice = TP.choose(caster, {}, "1:cloud-giant");
assert.equal(choice.action.id, "misty-step");
assert.deepEqual(choice.destination, state.position);
console.log("Browser in-place teleport resource-availability regression passed.");
