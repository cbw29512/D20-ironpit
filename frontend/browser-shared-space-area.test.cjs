"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), {filename:name},
);
window.IRON_PIT_BROWSER_GRID_GEOMETRY = {
  occupiedCells: (position) => [[position.x, position.y]],
};
load("browser-area-shapes.js");
load("browser-area-targeting.js");

const member = (id, side, x, y) => ({
  combatant_id: id, side, state: {
    position: {x,y}, is_alive: true, is_dead: false,
    current_hp: 90, template: {id, name:id, size:"medium"},
  },
});
const owner = member("generic-owner","monsters",3,3);
const overlapping = member("overlapping","heroes",3,3);
const adjacent = member("adjacent","heroes",4,3);
const ally = member("ally","monsters",3,3);
const setup = {
  heroes:[overlapping,adjacent], monsters:[owner,ally],
  map_definition:{width_squares:8,height_squares:8,cell_size_ft:5},
};
const area = {shape:"shared-space",origin:"self"};
const A = window.IRON_PIT_BROWSER_AREA_TARGETING;
const found = A.legalPlacements(owner,setup,area,0);
assert.equal(found.length,1);
assert.deepEqual(found[0].targetIds,["overlapping"]);
assert.deepEqual(found[0].friendlyIds,["ally"]);
assert.equal(A.memberInPlacement(owner,overlapping,area,found[0]),true);
assert.equal(A.memberInPlacement(owner,adjacent,area,found[0]),false);
const shifted = member("renamed-homebrew","monsters",1,1);
assert.deepEqual(A.legalPlacements(shifted,{
  ...setup,monsters:[shifted],heroes:[overlapping,adjacent],
},area,0),[]);
console.log("Universal shared-space target parity passed.");
