"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-distance-attack-disadvantage.js"), "utf8"),
  { filename: "browser-distance-attack-disadvantage.js" },
);

const state = {
  template: {
    name: "Cyclops",
    attack_disadvantage_beyond_ft: 30,
  },
};

const source = window.IRON_PIT_BROWSER_DISTANCE_ATTACK_DISADVANTAGE;
assert.equal(source.sources(state, 30), 0);
assert.equal(source.sources(state, 31), 1);
assert.equal(source.sources(state, 120), 1);
assert.equal(source.sources({ template: { name: "No Threshold" } }, 120), 0);

console.log("Browser distance-based attack Disadvantage uses the source-owned threshold.");
