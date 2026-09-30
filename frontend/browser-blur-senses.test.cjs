"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

load("browser-defensive-modifier-rules.js");

const state = {
  active_modifiers: [{
    id: "druid:blur:druid:0",
    kind: "attacks-against-disadvantage",
    source_effect_id: "blur",
    source_name: "Blur",
    source_creature_types: [],
    bypass_attacker_senses: ["blindsight", "truesight"],
  }],
};
const D = window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS;

assert.equal(D.attacksAgainstDisadvantage(state, { blindsight_ft: 0, truesight_ft: 0 }, 5), 1);
assert.equal(D.attacksAgainstDisadvantage(state, { blindsight_ft: 10, truesight_ft: 0 }, 5), 0);
assert.equal(D.attacksAgainstDisadvantage(state, { blindsight_ft: 10, truesight_ft: 0 }, 10), 0);
assert.equal(D.attacksAgainstDisadvantage(state, { blindsight_ft: 10, truesight_ft: 0 }, 15), 1);
assert.equal(D.attacksAgainstDisadvantage(state, { blindsight_ft: 0, truesight_ft: 60 }, 60), 0);
assert.equal(D.attacksAgainstDisadvantage(state, { blindsight_ft: 0, truesight_ft: 60 }, 65), 1);

console.log("Browser Blur special-sense bypass regressions passed.");
