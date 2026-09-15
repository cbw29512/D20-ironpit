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

const action = {
  id: "advanced-swallow",
  name: "Swallow",
  actionCost: "bonus_action",
  maxSwallowedTargets: 2,
  requiresGrappledTarget: false,
  maxTargetSize: "medium",
  firstTickDelayRounds: 0,
  totalCoverFromOutside: true,
};
const source = {
  combatant_id: "source",
  side: "monsters",
  position_ft: 5,
  state: {
    action_available: false,
    bonus_action_available: true,
    position: 1,
    template: { name: "Advanced Swallower", swallow_actions: [action] },
  },
};
const makeTarget = (id) => ({
  combatant_id: id,
  side: "heroes",
  position_ft: 5,
  state: {
    is_alive: true,
    is_dead: false,
    swallowed: null,
    grapple_sources: [],
    position: 1,
    active_effect_ids: [],
    template: { name: id },
  },
});
const first = makeTarget("first");
const second = makeTarget("second");
const third = makeTarget("third");
const setup = { heroes: [first, second, third], monsters: [source] };

window.IRON_PIT_BROWSER_STATE = { sizeAtMost: () => true };
window.IRON_PIT_BROWSER_GRAPPLE = {
  release: () => { throw new Error("Advanced Swallow must not invent a grapple prerequisite."); },
};
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => Boolean(state[`${cost}_available`]),
  spend: (state, cost) => { state[`${cost}_available`] = false; },
};
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };

load("browser-swallow.js");

let picked = window.IRON_PIT_BROWSER_SWALLOW.choose(source, setup);
assert.ok(picked);
assert.equal(picked.target.combatant_id, "first");

let result = window.IRON_PIT_BROWSER_SWALLOW.resolve(1, 1, source, setup);
assert.equal(result.handled, true);
assert.equal(source.state.action_available, false);
assert.equal(source.state.bonus_action_available, false);
assert.equal(first.state.swallowed.action_id, "advanced-swallow");

source.state.bonus_action_available = true;
picked = window.IRON_PIT_BROWSER_SWALLOW.choose(source, setup);
assert.ok(picked);
assert.equal(picked.target.combatant_id, "second");
result = window.IRON_PIT_BROWSER_SWALLOW.resolve(2, 1, source, setup);
assert.equal(result.handled, true);
assert.equal(second.state.swallowed.action_id, "advanced-swallow");

source.state.bonus_action_available = true;
assert.equal(window.IRON_PIT_BROWSER_SWALLOW.choose(source, setup), null);

console.log("Browser advanced Swallow action-economy/capacity regression passed.");
