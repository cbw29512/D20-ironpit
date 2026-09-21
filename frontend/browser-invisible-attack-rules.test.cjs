"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

window.IRON_PIT_BROWSER_MODIFIERS = {
  attacksAgainstAdvantage: () => 0,
  effectiveSpeed: (state) => state.template.speed_ft || 30,
};
window.IRON_PIT_BROWSER_BARBARIAN2 = {
  attacksAgainstAdvantage: () => 0,
};
window.IRON_PIT_BROWSER_EXHAUSTION = { attackDisadvantage: () => 0 };
window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS = { attacksAgainstDisadvantage: () => 0 };
window.IRON_PIT_BROWSER_GRAPPLE = { attackDisadvantage: () => 0, speedIsZero: () => false };
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };

load("browser-condition-rules.js");
load("browser-attack.js");

function state() {
  return {
    template: { speed_ft: 30, damage_immunities: [], damage_resistances: [], damage_vulnerabilities: [] },
    active_effect_ids: [],
    temporary_damage_resistances: [],
    is_unconscious: false,
  };
}

{
  const attacker = state(), defender = state();
  attacker.active_effect_ids.push("invisible");
  assert.deepEqual(window.IRON_PIT_BROWSER_ATTACK.conditionSources(attacker, defender, 5, "defender"), {
    advantage: 1, disadvantage: 0,
  });
}

{
  const attacker = state(), defender = state();
  defender.active_effect_ids.push("invisible");
  assert.deepEqual(window.IRON_PIT_BROWSER_ATTACK.conditionSources(attacker, defender, 5, "defender"), {
    advantage: 0, disadvantage: 1,
  });
}

{
  const attacker = state(), defender = state();
  attacker.active_effect_ids.push("invisible");
  defender.active_effect_ids.push("invisible");
  assert.deepEqual(window.IRON_PIT_BROWSER_ATTACK.conditionSources(attacker, defender, 5, "defender"), {
    advantage: 1, disadvantage: 1,
  });
}

console.log("Invisible uses the universal Advantage/Disadvantage attack pipeline.");
