"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

const mover = { combatant_id: "mover", state: { position: { x: 0, y: 0 } } };
const helpers = {
  position: (member) => member.state.position,
  occupantsAt: () => [],
  movementStepCostFt: (_map, _mover, destination) => (
    destination.x >= 0 && destination.x < 4 && destination.y >= 0 && destination.y < 4 ? 5 : null
  ),
};
window.IRON_PIT_BROWSER_GRID_PATH_SEARCH_SUPPORT = {
  keyOf: (position) => `${position.x},${position.y}`,
  reconstruct: (endKey, previous) => {
    const path = [];
    let cursor = endKey;
    while (previous.has(cursor)) {
      const [x, y] = cursor.split(",").map(Number);
      path.push({ x, y });
      cursor = previous.get(cursor);
    }
    return path.reverse();
  },
};

load("browser-grid-path-search.js");

const plans = window.IRON_PIT_BROWSER_GRID_PATH_SEARCH.reachableDestinations(
  { width_squares: 4, height_squares: 4, cell_size_ft: 5 },
  mover,
  [mover],
  10,
  helpers,
);
const byDestination = new Map(plans.map((plan) => [`${plan.destination.x},${plan.destination.y}`, plan]));

assert.equal(byDestination.get("0,0").movement_cost_ft, 0);
assert.equal(byDestination.get("1,0").movement_cost_ft, 5);
assert.equal(byDestination.get("2,0").movement_cost_ft, 10);
assert.deepEqual(byDestination.get("2,0").path, [{ x: 1, y: 0 }, { x: 2, y: 0 }]);
assert.equal(byDestination.has("3,0"), false);

console.log("Browser reachable-grid destination regression passed.");
