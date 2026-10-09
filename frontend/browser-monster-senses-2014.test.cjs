"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-monsters-2014.js"), "utf8"));
const roster = window.IRON_PIT_BROWSER_MONSTERS_2014;
assert.equal(Object.keys(roster).length, 203);
assert.equal(roster["2014-giant-scorpion"].blindsight_ft, 60);
assert.equal(roster["2014-half-red-dragon-veteran"].blindsight_ft, 10);
assert.equal(roster["2014-giant-scorpion"].truesight_ft, 0);
assert.equal(roster["2014-deva"]?.truesight_ft ?? 0, 0);
assert.equal(roster["2014-twig-blight"].blindsight_ft, 0,
  "blind-beyond caveat requires a distinct sight predicate before binding");
assert.ok(Object.values(roster).some((x) => x.blindsight_ft > 0));
console.log("2014 special senses source/export parity passed.");
