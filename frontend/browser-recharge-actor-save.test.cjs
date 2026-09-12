"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

const member = {
  combatant_id: "attacker",
  state: {
    resources: { recharge: 1 },
    template: {
      resourceDefinitions: { recharge: { recharge: { minimum: 5 } } },
      saving_throw_actions: [{ id: "recharge-save", resourceId: "recharge", resourceCost: 1, range: 5 }],
    },
  },
};
const target = { combatant_id: "target", state: {} };
const setup = { heroes: [member], monsters: [target] };

window.IRON_PIT_BROWSER_FORMATION = {
  targetOrder: () => [target],
  saveDistance: () => 5,
  chooseRechargeAttack: () => null,
};
window.IRON_PIT_BROWSER_RESOURCES = { available: () => true };
window.IRON_PIT_BROWSER_SAVES = {
  legalAction: (_action, _target, _distance, actor) => actor === member,
};
window.IRON_PIT_BROWSER_STATE = {};
window.IRON_PIT_BROWSER_CHARGE = {};
window.IRON_PIT_BROWSER_AREA_TARGETING = { legalPlacements: () => [] };
window.IRON_PIT_BROWSER_SAVE_TARGETS = {};
window.IRON_PIT_BROWSER_OFFENSE_VALUE = { saveAction: () => 0 };
window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION = {};

load("browser-recharge-action.js");

const choice = window.IRON_PIT_BROWSER_RECHARGE_ACTION.rechargeSaveChoice(member, setup);

assert.ok(choice);
assert.equal(choice.action.id, "recharge-save");
assert.equal(choice.target, target);

console.log("Browser Recharge actor-owned save regression passed.");
