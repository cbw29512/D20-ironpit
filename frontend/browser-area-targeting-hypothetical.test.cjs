"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
load("browser-grid-geometry.js");
load("browser-area-shapes.js");
load("browser-area-targeting.js");

const member = (id, side, x, y) => ({
  combatant_id: id,
  side,
  state: {
    position: { x, y }, is_alive: true, is_dead: false, current_hp: 10,
    template: { size: "medium" },
  },
});
const actor = member("actor", "heroes", 0, 0);
const target = member("target", "monsters", 2, 0);
const setup = {
  heroes: [actor], monsters: [target],
  map_definition: { id: "test", width_squares: 6, height_squares: 4, cell_size_ft: 5 },
};
const area = { shape: "emanation", origin: "self", radiusFt: 5 };

assert.deepEqual(window.IRON_PIT_BROWSER_AREA_TARGETING.legalPlacements(actor, setup, area, 0), []);
const placements = window.IRON_PIT_BROWSER_AREA_TARGETING.legalPlacements(
  actor,
  setup,
  area,
  0,
  { x: 1, y: 0 },
);

assert.ok(placements.length);
assert.deepEqual(placements[0].targetIds, ["target"]);
assert.deepEqual(actor.state.position, { x: 0, y: 0 });

console.log("Browser hypothetical area targeting regression passed.");
