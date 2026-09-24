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

const protectedTypes = ["aberration", "celestial", "elemental", "fey", "fiend", "undead"];
const template = {
  id: "aurelia-brightshield-2014-l15",
  name: "Aurelia Brightshield",
  passive_modifier_grants: [
    {
      source_id: "purity-of-spirit",
      source_name: "Purity of Spirit",
      kind: "attacks-against-disadvantage",
      condition_id: null,
      source_creature_types: protectedTypes,
    },
    {
      source_id: "purity-of-spirit",
      source_name: "Purity of Spirit",
      kind: "condition-immunity",
      condition_id: "charmed",
      source_creature_types: protectedTypes,
    },
    {
      source_id: "purity-of-spirit",
      source_name: "Purity of Spirit",
      kind: "condition-immunity",
      condition_id: "frightened",
      source_creature_types: protectedTypes,
    },
  ],
};

const rules = window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS;
const first = { template, active_modifiers: window.IRON_PIT_BROWSER_OPENING_MODIFIERS.build(template) };

assert.equal(first.active_modifiers.length, 3);
assert.equal(rules.attacksAgainstDisadvantage(first, { creature_type: "fiend" }), 1);
assert.equal(rules.attacksAgainstDisadvantage(first, { creature_type: "humanoid" }), 0);
assert.equal(rules.conditionImmune(first, "charmed", { creature_type: "undead" }), true);
assert.equal(rules.conditionImmune(first, "frightened", { creature_type: "fey" }), true);
assert.equal(rules.conditionImmune(first, "charmed", { creature_type: "humanoid" }), false);
assert.ok(first.active_modifiers.every((item) => item.source_effect_id === "purity-of-spirit"));
assert.ok(first.active_modifiers.every((item) => item.source_name === "Purity of Spirit"));

first.active_modifiers.length = 0;
const rebuilt = { template, active_modifiers: window.IRON_PIT_BROWSER_OPENING_MODIFIERS.build(template) };
assert.equal(first.active_modifiers.length, 0);
assert.equal(rebuilt.active_modifiers.length, 3);

console.log("2014 Paladin level 15 Purity of Spirit passive parity passed.");
