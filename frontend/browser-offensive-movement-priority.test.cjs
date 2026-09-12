"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

window.IRON_PIT_ACTION_ECONOMY = { available: () => true };
window.IRON_PIT_BROWSER_FORMATION = { targetOrder: (_member, setup) => setup.monsters };
window.IRON_PIT_BROWSER_STATE = { distance: () => 120 };
window.IRON_PIT_BROWSER_REACTION_MOVEMENT = {};

const actor = {
  combatant_id: "actor",
  state: { position: { x: 0, y: 0 }, movement_remaining_ft: 30 },
};
const target = {
  combatant_id: "target",
  state: { position: { x: 20, y: 0 } },
};
const setup = { heroes: [actor], monsters: [target], map_definition: {} };

load("browser-offensive-movement.js");
const movement = window.IRON_PIT_BROWSER_OFFENSIVE_MOVEMENT;

{
  window.IRON_PIT_BROWSER_OFFENSIVE_RANGES = {
    rangesForTarget: () => [
      { family: "ranged", priority: 1, executionRank: 2, maxRange: 320, preferredRange: 80 },
      { family: "spell", priority: 1, executionRank: 1, maxRange: 60, preferredRange: 60 },
    ],
  };
  window.IRON_PIT_BROWSER_GRID_MOVEMENT = {
    planToward: (_map, _actor, _target, _members, desired) => ({
      goal_reachable: true,
      path: [{ x: 1, y: 0 }],
      final_distance_ft: 90,
      movement_cost_ft: desired === 80 ? 5 : 30,
    }),
  };
  const intent = movement.chooseIntent(actor, setup, "1:actor");
  assert.equal(intent.family, "spell");
  assert.equal(intent.desiredDistanceFt, 60);
}

{
  window.IRON_PIT_BROWSER_STATE.distance = () => 100;
  window.IRON_PIT_BROWSER_OFFENSIVE_RANGES.rangesForTarget = () => [
    { family: "ranged", priority: 1, executionRank: 2, maxRange: 320, preferredRange: 80 },
  ];
  window.IRON_PIT_BROWSER_GRID_MOVEMENT.planToward = () => ({
    goal_reachable: true,
    path: [{ x: 1, y: 0 }],
    final_distance_ft: 70,
    movement_cost_ft: 30,
  });
  const intent = movement.chooseIntent(actor, setup, "1:actor");
  assert.equal(intent.family, "ranged");
  assert.equal(intent.desiredDistanceFt, 80);
}

{
  window.IRON_PIT_BROWSER_GRID_MOVEMENT.planToward = () => ({
    goal_reachable: false,
    path: [],
    final_distance_ft: 100,
    movement_cost_ft: 0,
  });
  assert.equal(movement.chooseIntent(actor, setup, "1:actor"), null);
}

console.log("Browser offensive movement priority regressions passed.");
