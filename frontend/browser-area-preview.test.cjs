"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
for (const file of ["browser-area-shapes.js", "browser-area-preview.js"]) {
  vm.runInThisContext(fs.readFileSync(path.join(__dirname, file), "utf8"), { filename: file });
}
const P = window.IRON_PIT_BROWSER_AREA_PREVIEW;
const map = { width_squares: 3, height_squares: 4 };
const blast = P.preview(map, { shape: "radius", radiusFt: 5 },
  { origin: [7.5, 7.5], targetIds: ["enemy"], friendlyIds: ["ally"] }, { flavor: "fire" });
assert.deepEqual(blast.cells, [{ x: 1, y: 0 }, { x: 0, y: 1 }, { x: 1, y: 1 }, { x: 2, y: 1 }, { x: 1, y: 2 }]);
assert.deepEqual(blast.targetIds, ["enemy"]);
assert.deepEqual(blast.friendlyIds, ["ally"]);
assert.equal(blast.color, P.COLORS.fire);
const bolt = P.preview(map, { shape: "line", lengthFt: 20, widthFt: 5 },
  { origin: [2.5, 2.5], direction: [0, 1] }, { flavor: "lightning" });
assert.deepEqual(bolt.cells, [{ x: 0, y: 0 }, { x: 0, y: 1 }, { x: 0, y: 2 }, { x: 0, y: 3 }]);
assert.equal(bolt.color, P.COLORS.lightning);
console.log("Area preview data-only geometry and ally/enemy metadata passed.");
