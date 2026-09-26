"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
window.IRON_PIT_BROWSER_MODIFIERS = { attacksAgainstAdvantage: () => 0, effectiveSpeed: () => 30 };
window.IRON_PIT_BROWSER_BARBARIAN2 = { attacksAgainstAdvantage: () => 0 };
window.IRON_PIT_BROWSER_EXHAUSTION = { attackDisadvantage: () => 0 };
window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS = { attacksAgainstDisadvantage: () => 0 };
window.IRON_PIT_BROWSER_GRAPPLE = { attackDisadvantage: () => 0, speedIsZero: () => false };
window.IRON_PIT_BROWSER_CONDITION_RULES = {
  has: (state, id) => state.active_effect_ids.includes(id),
  incapacitated: () => false,
  attackAdvantage: () => 0,
  autoCritical: () => false,
  suppressAttackAdvantage: () => false,
};

vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-attack.js"), "utf8"),
  { filename: "browser-attack.js" },
);

const state = (template, effects = []) => ({
  template,
  active_effect_ids: [...effects],
  timed_effects: [],
  is_unconscious: false,
});

const normal = state({ ignore_unseen_target_attack_disadvantage: false }, ["blinded"]);
const feral = state({ ignore_unseen_target_attack_disadvantage: true }, ["blinded"]);
const invisibleTarget = state({}, ["invisible"]);

assert.deepEqual(
  window.IRON_PIT_BROWSER_ATTACK.conditionSources(normal, invisibleTarget, 30, "target"),
  { advantage: 0, disadvantage: 2 },
);
assert.deepEqual(
  window.IRON_PIT_BROWSER_ATTACK.conditionSources(feral, invisibleTarget, 30, "target"),
  { advantage: 0, disadvantage: 0 },
);

feral.active_effect_ids.push("poisoned");
assert.deepEqual(
  window.IRON_PIT_BROWSER_ATTACK.conditionSources(feral, invisibleTarget, 30, "target"),
  { advantage: 0, disadvantage: 1 },
);
