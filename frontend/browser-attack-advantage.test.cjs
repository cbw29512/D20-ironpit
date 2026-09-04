"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const context = {
  console,
  IRON_PIT_BROWSER_MODIFIERS: {
    attacksAgainstAdvantage: () => 0,
    effectiveSpeed: (state) => state.template.speed_ft,
  },
  IRON_PIT_BROWSER_BARBARIAN2: {
    attacksAgainstAdvantage: () => 0,
  },
  IRON_PIT_BROWSER_GRAPPLE: {
    attackDisadvantage: () => 0,
    speedIsZero: () => false,
  },
  IRON_PIT_BROWSER_CONDITION_RULES: {
    has: (state, id) => state.active_effect_ids.includes(id),
    incapacitated: () => false,
    attackAdvantage: () => false,
  },
};
context.window = context;
vm.createContext(context);
vm.runInContext(
  fs.readFileSync(path.join(__dirname, "browser-attack.js"), "utf8"),
  context,
  { filename: "browser-attack.js" },
);

const attacker = {
  template: {
    max_hp: 22,
    speed_ft: 30,
    attack_roll_advantage_triggers: ["target_missing_hit_points"],
  },
  current_hp: 22,
  active_effect_ids: [],
};
const defender = {
  template: { max_hp: 22, speed_ft: 30 },
  current_hp: 22,
  active_effect_ids: [],
};

assert.deepEqual(
  JSON.parse(JSON.stringify(context.IRON_PIT_BROWSER_ATTACK.conditionSources(attacker, defender, 5, "target"))),
  { advantage: 0, disadvantage: 0 },
  "full-HP targets must not activate the missing-HP trigger",
);

defender.current_hp = 21;
assert.deepEqual(
  JSON.parse(JSON.stringify(context.IRON_PIT_BROWSER_ATTACK.conditionSources(attacker, defender, 5, "target"))),
  { advantage: 1, disadvantage: 0 },
  "any missing HP must activate Advantage, even above the Bloodied threshold",
);

attacker.active_effect_ids.push("poisoned");
assert.deepEqual(
  JSON.parse(JSON.stringify(context.IRON_PIT_BROWSER_ATTACK.conditionSources(attacker, defender, 5, "target"))),
  { advantage: 1, disadvantage: 1 },
  "the shared source calculation must preserve normal Advantage/Disadvantage cancellation",
);

console.log("browser missing-HP attack Advantage regression passed");
