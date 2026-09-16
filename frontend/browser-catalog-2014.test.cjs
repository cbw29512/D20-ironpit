"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

load("browser-monsters-2014.js");
load("browser-catalog.js");

(async () => {
  const catalog = await window.IRON_PIT_BROWSER_CATALOG.buildCatalog("2014");
  assert.equal(catalog.ruleset, "2014");
  assert.equal(catalog.test_lane, true);
  assert.equal(catalog.monster_count, 327);
  assert.equal(catalog.monster_ready_count, 100);
  assert.equal(catalog.heroes.length, 100);
  assert.equal(catalog.monsters.length, 100);
  assert.ok(catalog.heroes.every((card) => card.ruleset === "2014"));
  assert.ok(catalog.monsters.every((card) => card.ruleset === "2014"));
  console.log("2014 catalog accepts the full 100-monster certified browser roster.");
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
