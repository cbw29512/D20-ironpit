"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

load("browser-opening-modifiers.js");
load("browser-debuff-counters.js");

const counters = [
  ["difficult-terrain", "any", "prevent", 0],
  ["speed-reduction", "magical", "prevent", 0],
  ["restrained", "magical", "prevent", 0],
  ["grappled", "nonmagical", "remove-with-movement", 5],
  ["restrained", "nonmagical", "remove-with-movement", 5],
];
const template = {
  id: "renamed-source-card",
  passive_debuff_counter_grants: counters.map((entry, index) => ({
    source_id: `passive-freedom-of-movement-${index}`,
    source_name: "Freedom of Movement",
    counter: {
      debuff_id: entry[0], source_scope: entry[1],
      mode: entry[2], movement_cost_ft: entry[3],
    },
  })),
};
const state = {
  template,
  timed_effects: [],
  active_modifiers: window.IRON_PIT_BROWSER_OPENING_MODIFIERS.build(template),
};
const runtime = window.IRON_PIT_BROWSER_DEBUFF_COUNTERS;

assert.equal(runtime.difficultTerrainMultiplier(state), 1);
assert.equal(runtime.prevented(state, "speed-reduction", { sourceIsMagical: true }), true);
assert.equal(runtime.prevented(state, "restrained", { sourceIsMagical: true }), true);
assert.equal(runtime.prevented(state, "paralyzed", { sourceIsMagical: true }), false);
assert.equal(runtime.prevented(state, "grappled", { sourceIsMagical: false }), false);
assert.equal(runtime.movementCost(state, "grappled", { sourceIsMagical: false }), 5);
assert.equal(runtime.movementCost(state, "restrained", { sourceIsMagical: false }), 5);
assert.equal(runtime.movementCost(state, "grappled", { sourceIsMagical: true }), null);

console.log("Passive Freedom of Movement browser parity passed.");
