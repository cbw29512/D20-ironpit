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

window.IRON_PIT_ACTION_ECONOMY = { available: () => true };
window.IRON_PIT_BROWSER_FORMATION = { targetOrder: (_member, setup) => setup.monsters };
window.IRON_PIT_BROWSER_STATE = { distance: () => 120 };
window.IRON_PIT_BROWSER_REACTION_MOVEMENT = { moveToward: () => ({ events: [], sequence: 1 }) };
window.IRON_PIT_BROWSER_OFFENSIVE_RANGES = {
  rangesForTarget: () => [
    { family: "spell", priority: 1, executionRank: 1, expectedValue: 4,
      maxRange: 90, preferredRange: 90 },
    { family: "spell", priority: 1, executionRank: 1, expectedValue: 12,
      maxRange: 60, preferredRange: 60 },
  ],
};
window.IRON_PIT_BROWSER_GRID_MOVEMENT = {
  planToward: (_map, _member, _target, _members, desiredDistance) => ({
    goal_reachable: true,
    path: [{ x: 1, y: 0 }],
    final_distance_ft: desiredDistance,
    movement_cost_ft: desiredDistance === 90 ? 10 : 30,
  }),
};

load("browser-offensive-movement.js");

const attacker = {
  combatant_id: "attacker",
  side: "heroes",
  state: { position: { x: 0, y: 0 }, movement_remaining_ft: 30 },
};
const target = {
  combatant_id: "target",
  side: "monsters",
  state: { position: { x: 20, y: 0 } },
};
const setup = {
  heroes: [attacker],
  monsters: [target],
  map_definition: { width_squares: 24, height_squares: 16 },
};

const intent = window.IRON_PIT_BROWSER_OFFENSIVE_MOVEMENT.chooseIntent(
  attacker,
  setup,
  "1:attacker",
);

assert.ok(intent);
assert.equal(intent.family, "spell");
assert.equal(intent.desiredDistanceFt, 60);

console.log("Browser value-aware offensive movement regression passed.");
