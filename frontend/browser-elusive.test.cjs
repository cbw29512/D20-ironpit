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

window.IRON_PIT_BROWSER_CONDITION_RULES = {
  incapacitated: (state) => state.is_unconscious || state.active_effect_ids.includes("incapacitated"),
};

load("browser-attack-advantage.js");

const target = {
  template: {
    max_hp: 183,
    attack_advantage_suppressed_unless_incapacitated: true,
  },
  current_hp: 183,
  max_hp_bonus: 0,
  is_unconscious: false,
  active_effect_ids: [],
};

assert.equal(window.IRON_PIT_BROWSER_ATTACK_ADVANTAGE.suppress(3, target), 0);
assert.equal(window.IRON_PIT_BROWSER_ATTACK_ADVANTAGE.suppress(0, target), 0);

target.active_effect_ids.push("incapacitated");
assert.equal(window.IRON_PIT_BROWSER_ATTACK_ADVANTAGE.suppress(3, target), 3);

target.active_effect_ids.length = 0;
target.template.attack_advantage_suppressed_unless_incapacitated = false;
assert.equal(window.IRON_PIT_BROWSER_ATTACK_ADVANTAGE.suppress(3, target), 3);

console.log("Browser generic defender Advantage suppression regressions passed.");
