"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_SOURCE_EFFECT_IMMUNITY = { immune: () => false, grant: () => {} };
window.IRON_PIT_BROWSER_CONDITION_RULES = { incapacitated: () => false };
window.IRON_PIT_DICE = { roll: () => 1 };

load("browser-timed-conditions.js");
load("browser-save-control-effects.js");
load("browser-action-economy.js");
load("browser-modifiers.js");

function state(name) {
  return {
    is_alive: true, is_dead: false, is_unconscious: false,
    action_available: true, bonus_action_available: true, reaction_available: true,
    timed_effects: [], active_effect_ids: [], active_modifiers: [],
    template: { name, ruleset: "2014", speed_ft: 30, armor_class: 16 },
  };
}

const target = { combatant_id: "fighter", state: state("Fighter") };
const actor = { combatant_id: "dragon", state: { template: { name: "Copper Dragon" } } };
const action = {
  id: "slowing-breath",
  failureControlEffect: {
    effectId: "slowed", durationRounds: 10, expiryTiming: "target_turn_end",
    repeatSaveAbility: "constitution", repeatSaveDc: 14, repeatSaveTiming: "target_turn_end",
    speedMultiplier: 0.5, blocksReactions: true, actionBonusExclusive: true,
    maxAttacksPerTurn: 1,
  },
};

const applied = window.IRON_PIT_BROWSER_SAVE_CONTROL.applyOutcome(actor, target, action, false, 1);
assert.deepEqual(applied, ["slowed"]);
assert.equal(target.state.timed_effects[0].max_attacks_per_turn, 1);
assert.equal(window.IRON_PIT_BROWSER_MODIFIERS.effectiveSpeed(target.state), 15);
assert.equal(window.IRON_PIT_ACTION_ECONOMY.available(target.state, "reaction"), false);
assert.equal(window.IRON_PIT_ACTION_ECONOMY.available(target.state, "action"), true);
assert.equal(window.IRON_PIT_ACTION_ECONOMY.available(target.state, "bonus_action"), true);
window.IRON_PIT_ACTION_ECONOMY.spend(target.state, "action");
assert.equal(window.IRON_PIT_ACTION_ECONOMY.available(target.state, "bonus_action"), false);

const weakened = { combatant_id: "weakened", state: state("Weakened Fighter") };
const gold = { combatant_id: "gold-dragon", state: { template: { name: "Gold Dragon" } } };
const weakening = {
  id: "weakening-breath",
  failureControlEffect: {
    effectId: "weakened-strength", durationRounds: 10, expiryTiming: "target_turn_end",
    repeatSaveAbility: "strength", repeatSaveDc: 14, repeatSaveTiming: "target_turn_end",
    disadvantageStrengthD20Tests: true,
  },
};
assert.deepEqual(window.IRON_PIT_BROWSER_SAVE_CONTROL.applyOutcome(gold, weakened, weakening, false, 1), ["weakened-strength"]);
assert.equal(weakened.state.timed_effects[0].disadvantage_strength_d20_tests, true);
assert.equal(window.IRON_PIT_BROWSER_TIMED.strengthD20Disadvantage(weakened.state), 1);
assert.equal(window.IRON_PIT_BROWSER_TIMED.strengthD20Disadvantage(target.state), 0);

console.log("2014 browser Slowing/Weakening Breath regressions passed.");