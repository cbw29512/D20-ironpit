"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
load("browser-grid-geometry.js");
load("browser-grid-movement.js");

const M = window.IRON_PIT_BROWSER_GRID_MOVEMENT;
const map = { id: "movement-test", width_squares: 8, height_squares: 8, cell_size_ft: 5 };

function member(id, side, x, y, size = "medium", incapacitated = false) {
  return {
    combatant_id: id,
    side,
    state: {
      position: { x, y },
      is_unconscious: incapacitated,
      template: { id, name: id, size },
    },
  };
}

const mover = member("mover", "heroes", 0, 0);
const ally = member("ally", "heroes", 1, 1);
const hostile = member("hostile", "monsters", 1, 1);
const incapacitated = member("incapacitated", "monsters", 1, 1, "medium", true);
const tiny = member("tiny", "monsters", 1, 1, "tiny");
const huge = member("huge", "monsters", 1, 1, "huge");

assert.equal(M.canPassThrough(mover, ally), true);
assert.equal(M.creatureSpaceIsDifficult(mover, ally), false);
assert.equal(M.canPassThrough(mover, hostile), false);
assert.equal(M.canPassThrough(mover, incapacitated), true);
assert.equal(M.creatureSpaceIsDifficult(mover, incapacitated), true);
assert.equal(M.canPassThrough(mover, tiny), true);
assert.equal(M.creatureSpaceIsDifficult(mover, tiny), false);
assert.equal(M.canPassThrough(mover, huge), true);
assert.equal(M.creatureSpaceIsDifficult(mover, huge), true);

assert.equal(M.movementStepCostFt(map, mover, { x: 1, y: 1 }, [mover]), 5);
assert.equal(M.movementStepCostFt(map, mover, { x: 1, y: 1 }, [mover, ally]), 5);
assert.equal(M.movementStepCostFt(map, mover, { x: 1, y: 1 }, [mover, hostile]), null);
assert.equal(M.movementStepCostFt(map, mover, { x: 1, y: 1 }, [mover, incapacitated]), 10);

const target = member("target", "monsters", 3, 3);
const plan = M.planToward(map, mover, target, [mover, target], 5, 30);
assert.deepEqual(plan.path, [{ x: 1, y: 1 }, { x: 2, y: 2 }]);
assert.equal(plan.movement_cost_ft, 10);
assert.equal(plan.final_distance_ft, 5);

const planAroundAlly = M.planToward(map, mover, target, [mover, ally, target], 5, 30);
assert.ok(planAroundAlly.path.length > 0);
assert.notDeepEqual(planAroundAlly.path.at(-1), { x: 1, y: 1 });
assert.equal(planAroundAlly.final_distance_ft, 5);

console.log("Grid movement browser parity regressions passed.");
