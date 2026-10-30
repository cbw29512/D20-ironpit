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

window.IRON_PIT_BROWSER_ROLLS = {
  d20: (_bonus, mode) => ({
    rolls: mode === "disadvantage" ? [18, 4] : [18],
    selected_roll: mode === "disadvantage" ? 4 : 18,
    total: mode === "disadvantage" ? 4 : 18,
    modifier: 0,
    mode,
  }),
  modeFromSources: (advantage, disadvantage) => (
    advantage && disadvantage ? "normal"
      : advantage ? "advantage"
        : disadvantage ? "disadvantage" : "normal"
  ),
};
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_CONDITION_RULES = { speedZero: () => false };
window.IRON_PIT_BROWSER_MODIFIERS = {
  abilityCheckDisadvantage: () => 0,
  applyD20Bonus: (_state, _kind, roll) => roll,
};
window.IRON_PIT_BROWSER_FRIGHTENED = { d20Disadvantage: () => 0 };
window.IRON_PIT_ACTION_ECONOMY = {
  available: () => true,
  spend: (state) => { state.action_available = false; },
};

load("browser-grapple.js");

const state = {
  template: {
    name: "Target",
    speed_ft: 30,
    skill_bonuses: { athletics: 0 },
    progression_features: { athletics_advantage: false },
  },
  active_effect_ids: [],
  timed_effects: [],
  grapple_sources: [],
  action_available: true,
  movement_remaining_ft: 0,
};

window.IRON_PIT_BROWSER_GRAPPLE.apply(
  state, "mimic", 13, 5, false, [], "pseudopod", true,
);
const event = window.IRON_PIT_BROWSER_GRAPPLE.escape(
  1, 1, { combatant_id: "target", state },
);

assert.equal(state.grapple_sources[0].escape_check_disadvantage, true);
assert.equal(event.ability_check_roll.mode, "disadvantage");
assert.equal(event.ability_check_roll.selected_roll, 4);

console.log("Browser grapple escape disadvantage parity passed.");
