"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-monsters-2014.js"), "utf8"),
  { filename: "browser-monsters-2014.js" },
);

const expected = {
  "2014-bronze-dragon-wyrmling": [12, 30],
  "2014-young-bronze-dragon": [15, 40],
};

for (const [monsterId, [dc, pushFt]] of Object.entries(expected)) {
  const monster = window.IRON_PIT_BROWSER_MONSTERS_2014[monsterId];
  assert.ok(monster, `${monsterId} must be in the certified browser roster.`);
  const repulsion = monster.saving_throw_actions.find(
    (action) => action.id === "repulsion-breath",
  );
  assert.ok(repulsion, `${monsterId} must serialize Repulsion Breath.`);
  assert.equal(repulsion.name, "Repulsion Breath");
  assert.equal(repulsion.saveAbility, "strength");
  assert.equal(repulsion.dc, dc);
  assert.equal(repulsion.failedSavePushFt, pushFt);
  assert.equal(repulsion.resourceId, "breath-weapons");
  assert.equal(repulsion.area.shape, "cone");
  assert.equal(repulsion.area.length_ft, 30);
}

console.log("Browser Bronze Repulsion Breath binds shared failed-save forced movement.");
