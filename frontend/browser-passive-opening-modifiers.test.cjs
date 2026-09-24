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

load("browser-opening-modifiers.js");
load("browser-defensive-modifier-rules.js");

const O = window.IRON_PIT_BROWSER_OPENING_MODIFIERS;
const D = window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS;

const template = {
  id: "aurelia-15",
  passive_modifier_grants: [{
    sourceId: "purity-of-spirit",
    sourceName: "Purity of Spirit",
    modifierEffects: [
      {
        kind: "attacks-against-disadvantage",
        flatBonus: 0,
        diceCount: 0,
        diceSize: 0,
        damageType: null,
        sourceCreatureTypes: ["aberration", "celestial", "elemental", "fey", "fiend", "undead"],
      },
      {
        kind: "condition-immunity",
        flatBonus: 0,
        diceCount: 0,
        diceSize: 0,
        damageType: null,
        conditionId: "charmed",
        sourceCreatureTypes: ["aberration", "celestial", "elemental", "fey", "fiend", "undead"],
      },
      {
        kind: "condition-immunity",
        flatBonus: 0,
        diceCount: 0,
        diceSize: 0,
        damageType: null,
        conditionId: "frightened",
        sourceCreatureTypes: ["aberration", "celestial", "elemental", "fey", "fiend", "undead"],
      },
    ],
  }],
};

const state = { active_modifiers: O.build(template) };
const fiend = { creature_type: "fiend" };
const humanoid = { creature_type: "humanoid" };

assert.equal(state.active_modifiers.length, 3);
assert.equal(D.attacksAgainstDisadvantage(state, fiend), 1);
assert.equal(D.attacksAgainstDisadvantage(state, humanoid), 0);
assert.equal(D.conditionImmune(state, "charmed", fiend), true);
assert.equal(D.conditionImmune(state, "frightened", fiend), true);
assert.equal(D.conditionImmune(state, "charmed", humanoid), false);

console.log("Browser passive opening modifier parity passed.");
