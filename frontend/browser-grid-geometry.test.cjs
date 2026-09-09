const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-grid-geometry.js"), "utf8"),
  { filename: "browser-grid-geometry.js" },
);

const G = window.IRON_PIT_BROWSER_GRID_GEOMETRY;

assert.equal(G.footprintSide("tiny"), 1);
assert.equal(G.footprintSide("small"), 1);
assert.equal(G.footprintSide("medium"), 1);
assert.equal(G.footprintSide("large"), 2);
assert.equal(G.footprintSide("huge"), 3);
assert.equal(G.footprintSide("gargantuan"), 4);

assert.deepEqual(
  G.occupiedCells({ x: 3, y: 4 }, "large"),
  [[3, 4], [3, 5], [4, 4], [4, 5]],
);

const map = { id: "iron-pit-test", width_squares: 10, height_squares: 10, cell_size_ft: 5 };
assert.equal(G.inBounds(map, { x: 7, y: 7 }, "huge"), true);
assert.equal(G.inBounds(map, { x: 8, y: 8 }, "huge"), false);

assert.equal(G.overlaps({ x: 2, y: 2 }, "large", { x: 3, y: 3 }, "medium"), true);
assert.equal(G.overlaps({ x: 2, y: 2 }, "large", { x: 4, y: 4 }, "medium"), false);

assert.equal(G.footprintDistanceFt({ x: 0, y: 0 }, "medium", { x: 1, y: 1 }, "medium"), 5);
assert.equal(G.footprintDistanceFt({ x: 0, y: 0 }, "large", { x: 3, y: 0 }, "large"), 10);

console.log("browser grid geometry regression passed");
