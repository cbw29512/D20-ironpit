"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
load("browser-grid-geometry.js");
load("browser-formation.js");
load("browser-formation-rows.js");
load("browser-arena-map.js");
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

const arena = window.IRON_PIT_BROWSER_ARENA_MAP;
for (const [side, zone, expectedFrontX] of [
  ["heroes", arena.buildHeroDeploymentZone(), 9],
  ["monsters", arena.buildMonsterDeploymentZone(), 14],
]) {
  const dragons = Array.from({ length: 6 }, (_, i) => member(`${side}-dragon-${i}`, "gargantuan"));
  dragons.forEach((dragon) => { dragon.side = side; });
  const packed = P.packZone(map, zone, dragons);
  P.apply(dragons, packed);
  const occupied = new Set(dragons.map((dragon) => `${dragon.state.position.x},${dragon.state.position.y}`));
  assert.equal(occupied.size, 6);
  assert.equal(dragons.filter((dragon) => dragon.state.formation_row === "front").length, 3);
  assert.equal(dragons.filter((dragon) => dragon.state.formation_row === "back").length, 3);
  assert.ok(dragons.filter((dragon) => dragon.state.formation_row === "front")
    .every((dragon) => dragon.state.position.x === expectedFrontX));
  for (let x = zone.x; x < zone.x + 2; x += 1) {
    for (let y = zone.y; y < zone.y + 3; y += 1) assert.ok(occupied.has(`${x},${y}`));
  }
}
assert.equal((arena.buildMonsterDeploymentZone().x - 9) * 5, 25);
console.log("Hybrid 3x2 starting formations fit six Gargantuan combatants per side.");
