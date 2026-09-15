"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

window.IRON_PIT_BROWSER_GRID_GEOMETRY = {};
window.IRON_PIT_BROWSER_FRIGHTENED = { sources: () => [] };
window.IRON_PIT_BROWSER_GRID_MOVEMENT_SUPPORT = { movementStepCostFt: () => 5 };
window.IRON_PIT_BROWSER_REACTIONS = { resolveOpportunityAttack: () => null };
window.IRON_PIT_BROWSER_GRAPPLE = { speedIsZero: () => false };
load("browser-grid-reaction-support.js");

const mover = {
  combatant_id: "mover",
  side: "heroes",
  state: {
    position: { x: 0, y: 0 }, movement_remaining_ft: 10,
    active_effect_ids: [], is_dead: false, is_unconscious: false,
    template: { name: "Mover", size: "medium" },
  },
};
const setup = {
  heroes: [mover], monsters: [],
  map_definition: { id: "test", width_squares: 4, height_squares: 4, cell_size_ft: 5 },
};

const result = window.IRON_PIT_BROWSER_GRID_REACTION_SUPPORT.executePath(
  1,
  1,
  mover,
  setup,
  [{ x: 1, y: 0 }, { x: 2, y: 0 }],
);

assert.equal(result.sequence, 3);
assert.equal(result.events.length, 2);
assert.deepEqual(mover.state.position, { x: 2, y: 0 });
assert.equal(mover.state.movement_remaining_ft, 0);
assert.equal(result.events.every((event) => event.target_id == null), true);

console.log("Browser targetless grid path execution regression passed.");
