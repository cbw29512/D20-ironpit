"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

load("browser-effective-senses.js");
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
const S = window.IRON_PIT_BROWSER_EFFECTIVE_SENSES;

assert.equal(D.attacksAgainstDisadvantage(state, { blindsight_ft: 0, truesight_ft: 0 }, 5), 1);
assert.equal(D.attacksAgainstDisadvantage(state, { blindsight_ft: 10, truesight_ft: 0 }, 5), 0);
assert.equal(D.attacksAgainstDisadvantage(state, { blindsight_ft: 10, truesight_ft: 0 }, 10), 0);
assert.equal(D.attacksAgainstDisadvantage(state, { blindsight_ft: 10, truesight_ft: 0 }, 15), 1);
assert.equal(D.attacksAgainstDisadvantage(state, { blindsight_ft: 0, truesight_ft: 60 }, 60), 0);
assert.equal(D.attacksAgainstDisadvantage(state, { blindsight_ft: 0, truesight_ft: 60 }, 65), 1);

const hearing = {
  active_effect_ids: [],
  active_modifiers: [],
  timed_effects: [],
  blindsight_requires_hearing: true,
  template: {
    name: "Synthetic Hearing Blindsight",
    blindsight_ft: 60,
    truesight_ft: 0,
    blindsight_requires_hearing: true,
  },
};
assert.equal(S.effectiveSenseRangeFt(hearing, "blindsight"), 60);
assert.equal(D.attacksAgainstDisadvantage(state, hearing, 5), 0);
hearing.active_effect_ids.push("deafened");
assert.equal(S.effectiveSenseRangeFt(hearing, "blindsight"), 0);
assert.equal(S.sourceSenseRangeFt(hearing, "blindsight"), 60);
assert.equal(hearing.template.blindsight_ft, 60);
assert.equal(D.attacksAgainstDisadvantage(state, hearing, 5), 1);
hearing.active_effect_ids = [];
assert.equal(S.effectiveSenseRangeFt(hearing, "blindsight"), 60);
assert.equal(D.attacksAgainstDisadvantage(state, hearing, 5), 0);

const unnamed = {
  name: "Bat",
  active_effect_ids: ["deafened"],
  template: { name: "Bat", blindsight_ft: 60, truesight_ft: 0 },
};
assert.equal(S.effectiveSenseRangeFt(unnamed, "blindsight"), 60);
assert.equal(D.attacksAgainstDisadvantage(state, unnamed, 5), 0);

console.log("Browser Blur special-sense bypass regressions passed.");
