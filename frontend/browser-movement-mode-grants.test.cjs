"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
window.IRON_PIT_BROWSER_MODIFIERS = {
  effectiveSpeed: (state) => state.template.speed_ft,
};
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);
load("browser-state.js");

const template = {
  id: "movement-test", name: "Movement Test", speed_ft: 30,
  movement_modes: {
    walk_ft: 30, fly_ft: 0, climb_ft: 0, swim_ft: 0, burrow_ft: 0, hover: false,
  },
  max_hp: 10, resources: {}, traits: [],
};
const state = window.IRON_PIT_BROWSER_STATE.buildState(template);
assert.equal(window.IRON_PIT_BROWSER_STATE.effectiveMovementModes(state).fly_ft, 0);

state.timed_effects.push({
  effect_id: "dragon-wings",
  source_id: "hero",
  source_effect_id: "dragon-wings",
  owned_movement_mode_grants: [{
    mode: "fly", fixedSpeedFt: null, matchCurrentSpeed: true,
  }],
});
assert.equal(window.IRON_PIT_BROWSER_STATE.effectiveMovementModes(state).fly_ft, 30);
assert.equal(state.template.movement_modes.fly_ft, 0);

console.log("Browser temporary movement-mode grants preserve immutable printed movement.");
