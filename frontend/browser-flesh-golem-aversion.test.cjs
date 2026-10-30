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
window.IRON_PIT_DICE = { roll: () => 10 };
window.IRON_PIT_BROWSER_CONDITION_RULES = { has: () => false, attackAdvantage: () => false, incapacitated: () => false };
load("browser-modifiers.js");
load("browser-damage-taken-disadvantage.js");
load("browser-attack.js");

const state = {
  turn_serial: 3,
  active_modifiers: [],
  temporary_damage_resistances: [],
  template: {
    id: "srd-flesh-golem",
    name: "Flesh Golem",
    armor_class: 9,
    damage_absorption_types: [],
    damage_immunities: [],
    damage_resistances: [],
    damage_vulnerabilities: [],
    damage_taken_disadvantage_rules: [{
      id: "aversion-to-fire",
      name: "Aversion to Fire",
      damageType: "fire",
      attackRollDisadvantage: true,
      abilityCheckDisadvantage: true,
    }],
  },
};

assert.equal(window.IRON_PIT_BROWSER_ATTACK.adjustedDamage(state, 5, "fire"), 5);
assert.equal(window.IRON_PIT_BROWSER_MODIFIERS.attackRollDisadvantage(state), 1);
assert.equal(window.IRON_PIT_BROWSER_MODIFIERS.abilityCheckDisadvantage(state), 1);
assert.deepEqual(
  [...new Set(state.active_modifiers.map((item) => item.expires_target_turn_serial))],
  [4],
);

assert.equal(window.IRON_PIT_BROWSER_MODIFIERS.expireTargetTurn(state), 0);
state.turn_serial = 4;
assert.equal(window.IRON_PIT_BROWSER_MODIFIERS.expireTargetTurn(state), 2);
assert.equal(window.IRON_PIT_BROWSER_MODIFIERS.attackRollDisadvantage(state), 0);

state.template.damage_immunities = ["fire"];
assert.equal(window.IRON_PIT_BROWSER_ATTACK.adjustedDamage(state, 5, "fire"), 0);
assert.equal(state.active_modifiers.length, 0);

console.log("Browser Flesh Golem Aversion to Fire parity passed.");
