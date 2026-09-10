"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
load("browser-action-economy.js");
load("browser-timed-conditions.js");
load("browser-save-failure-effects.js");

const E = window.IRON_PIT_ACTION_ECONOMY;
const F = window.IRON_PIT_BROWSER_SAVE_FAILURE_EFFECTS;

const state = () => ({
  is_dead: false,
  is_alive: true,
  is_unconscious: false,
  turn_terminated: false,
  action_available: true,
  bonus_action_available: true,
  reaction_available: true,
  active_effect_ids: [],
  timed_effects: [],
});
const effect = {
  kind: "turn-restriction",
  actionOrBonusOnly: true,
  reactionsDisabled: true,
  expiryTiming: "target_turn_end",
};

{
  const target = { state: state() };
  assert.deepEqual(F.apply(target, "monster-1", "fetid-cloud", [effect], { round: 1 }), ["turn-restriction"]);
  assert.equal(E.available(target.state, "reaction"), false);
  E.spend(target.state, "action");
  assert.equal(E.available(target.state, "bonus_action"), false);
}

{
  const target = { state: state() };
  F.apply(target, "monster-1", "fetid-cloud", [effect], { round: 1 });
  E.spend(target.state, "bonus_action");
  assert.equal(E.available(target.state, "action"), false);
  assert.equal(target.state.timed_effects[0].expiry_timing, "target_turn_end");
}

console.log("Browser timed turn restriction regressions passed.");
