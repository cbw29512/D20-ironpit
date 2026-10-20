"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
window.IRON_PIT_BROWSER_GRID_GEOMETRY = {
  occupiedCells: (position) => [[position.x, position.y]],
};
load("browser-area-shapes.js");
load("browser-area-targeting.js");
const shape = window.IRON_PIT_BROWSER_AREA_SHAPES;
const origin = shape.cellCenterFt(5, 4);
for (const [x, y] of [[5,4], [6,4], [5,5], [6,5]]) {
  assert.equal(shape.squareContains(origin, shape.cellCenterFt(x,y),10), true);
}
for (const [x, y] of [[4,4], [7,4], [5,6], [6,3]]) {
  assert.equal(shape.squareContains(origin, shape.cellCenterFt(x,y),10), false);
}
const member = (id, side, x, y) => ({
  combatant_id: id, side,
  state: {
    position: { x, y }, is_alive: true, is_dead: false,
    current_hp: 20, template: { size: "medium" },
  },
});
const actor = member("actor","monsters",1,4);
const foe = member("foe","heroes",5,4);
const setup = {
  monsters: [actor], heroes: [foe],
  map_definition: { width_squares: 10, height_squares: 10 },
};
const area = { shape: "square", origin: "point", length_ft: 10 };
const places = window.IRON_PIT_BROWSER_AREA_TARGETING.legalPlacements(actor,setup,area,30);
const hits = places.filter(p=>p.targetIds.includes("foe"));
assert.ok(new Set(hits.map(p=>p.origin.join(","))).size>=2);
assert.ok(hits.every(p=>!p.targetIds.includes("actor")));
console.log("Square-area geometry preserves all legal landing origins.");
