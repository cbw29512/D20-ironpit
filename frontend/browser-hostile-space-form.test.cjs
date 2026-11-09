"use strict";

// A monster template, a renamed homebrew form and a pregen share this path.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), {filename:name},
);
for (const file of [
  "browser-grid-geometry.js", "browser-grid-barriers.js",
  "browser-grid-movement-support.js", "browser-grid-path-search-support.js",
  "browser-grid-path-search.js", "browser-grid-movement.js",
]) load(file);

const M = window.IRON_PIT_BROWSER_GRID_MOVEMENT;
const map = {id:"overlap",width_squares:8,height_squares:8,cell_size_ft:5};
function member(id, side, x, y) {
  return {combatant_id:id,side,state:{
    position:{x,y},is_alive:true,is_dead:false,is_unconscious:false,
    template:{id,name:id,size:"medium",source_allows_hostile_overlap:false},
  }};
}
const mover = member("generic-source-owner","monsters",0,0);
const target = member("victim","heroes",2,2);
const before = M.planToward(map,mover,target,[mover,target],0,30);
assert.ok(!before.path.length || JSON.stringify(before.path.at(-1)) !== '{"x":2,"y":2}');
mover.state.template.source_allows_hostile_overlap = true;
const result = M.planToward(
  map,mover,target,[mover,target],0,30,null,false,
  mover.state.template.source_allows_hostile_overlap,
);
assert.equal(result.goal_reachable,true);
assert.deepEqual(result.path.at(-1),{x:2,y:2});
assert.ok(result.movement_cost_ft > 0);
const ally = member("ally","monsters",2,2);
const noAllyStop = M.planToward(
  map,mover,target,[mover,target,ally],0,30,null,false,
  mover.state.template.source_allows_hostile_overlap,
);
assert.ok(!noAllyStop.path.length
  || JSON.stringify(noAllyStop.path.at(-1)) !== '{"x":2,"y":2}');
console.log("Hostile-space form movement parity passed.");
