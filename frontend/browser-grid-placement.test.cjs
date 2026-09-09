"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
load("browser-grid-geometry.js");
load("browser-formation.js");
load("browser-grid-placement.js");

const G = window.IRON_PIT_BROWSER_GRID_GEOMETRY;
const P = window.IRON_PIT_BROWSER_GRID_PLACEMENT;
const map = { id: "iron-pit-standard-vtt", width_squares: 24, height_squares: 16, cell_size_ft: 5 };
const zone = { x: 0, y: 2, width_squares: 8, height_squares: 12, front_edge: "east" };

function member(id, size = "medium") {
  return {
    combatant_id: id,
    side: "heroes",
    state: {
      position: null,
      template: {
        id, name: id, size, primary_attack_id: "claw",
        attacks: [{ id: "claw", kind: "melee", reach: 5 }],
        spell_attack_actions: [], spell_save_actions: [],
      },
    },
  };
}

const gargantuans = Array.from({ length: 6 }, (_, index) => member(`gargantuan-${index}`, "gargantuan"));
const assignments = P.packZone(map, zone, gargantuans);
P.apply(gargantuans, assignments);

assert.equal(assignments.length, 6);
assert.ok(gargantuans.every((item) => item.state.position));
for (let index = 0; index < gargantuans.length; index += 1) {
  const current = gargantuans[index];
  assert.equal(G.inBounds(map, current.state.position, current.state.template.size), true);
  for (const other of gargantuans.slice(index + 1)) {
    assert.equal(G.overlaps(
      current.state.position, current.state.template.size,
      other.state.position, other.state.template.size,
    ), false);
  }
}

console.log("Grid placement browser parity regressions passed.");
