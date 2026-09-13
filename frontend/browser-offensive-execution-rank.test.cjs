"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

window.IRON_PIT_ACTION_ECONOMY = { available: () => true };
window.IRON_PIT_BROWSER_SPELLCASTING = { actionResourceAvailable: () => true };
window.IRON_PIT_BROWSER_RESOURCES = { available: () => true };
window.IRON_PIT_BROWSER_CONDITION_RULES = { has: () => false };
window.IRON_PIT_BROWSER_STATE = { sizeAtMost: () => true };
window.IRON_PIT_BROWSER_OFFENSE_VALUE = { saveAction: () => 0 };
window.IRON_PIT_BROWSER_TIMED = { affectedByAction: () => false };

load("browser-offensive-ranges.js");

const attacker = {
  combatant_id: "attacker",
  state: {
    template: {
      resourceDefinitions: {},
      attack_action: {
        slots: [{ attackIds: ["multi-attack"], saveActionIds: ["multi-save"] }],
      },
      attacks: [
        { id: "multi-attack", kind: "melee", reach: 5 },
        { id: "standard-only", kind: "melee", reach: 5 },
      ],
      spell_attack_actions: [],
      spell_save_actions: [],
      automatic_spell_actions: [],
      saving_throw_actions: [
        { id: "multi-save", actionCost: "action", range: 30 },
        { id: "ordinary-save", actionCost: "action", range: 30 },
      ],
    },
  },
};
const target = {
  combatant_id: "target",
  state: { grapple_sources: [] },
};

const profiles = window.IRON_PIT_BROWSER_OFFENSIVE_RANGES.rangesForTarget(
  attacker,
  target,
  "1:attacker",
);

assert.deepEqual(profiles.map((profile) => profile.executionRank), [2, 4, 2, 3]);

console.log("Browser offensive resolver-stage rank regression passed.");
