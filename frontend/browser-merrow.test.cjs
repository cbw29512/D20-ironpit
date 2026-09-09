"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-monsters-generated.js"), "utf8"),
  { filename: "browser-monsters-generated.js" },
);

const merrow = window.IRON_PIT_BROWSER_MONSTERS["srd-merrow"];
assert.ok(merrow, "Certified Merrow must be present in generated browser runtime");
assert.deepEqual(merrow.attacks.map((attack) => attack.id), [
  "srd-merrow-bite",
  "srd-merrow-claw",
  "srd-merrow-harpoon-melee",
  "srd-merrow-harpoon-ranged",
]);
const harpoons = merrow.attacks.filter((attack) => attack.name === "Harpoon");
assert.deepEqual(harpoons.map((attack) => attack.kind), ["melee", "ranged"]);
assert.equal(harpoons[0].reach, 5);
assert.equal(harpoons[1].normal, 20);
assert.equal(harpoons[1].long, 60);
for (const attack of harpoons) {
  assert.deepEqual(attack.controlEffect, {
    maxTargetSize: "large",
    forcedMovement: { direction: "toward_source", maxDistanceFt: 15, distanceMode: "up_to" },
  });
}
