"use strict";
// Original printed parameters are data. Shared browser resolvers own runtime.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = (file) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, file), "utf8"), { filename: file },
);
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
load("browser-opening-modifiers.js");
load("browser-modifier-validation.js");
load("browser-modifiers.js");
load("browser-rolls.js");
load("browser-action-economy.js");
load("browser-condition-rules.js");
load("browser-timed-conditions.js");
load("browser-timed-condition-lifecycle.js");
load("browser-concentration.js");
load("browser-timed-self-buff-policy.js");
load("browser-timed-self-buffs.js");
load("browser-state.js");
load("browser-ability-checks.js");
load("browser-defensive-modifier-rules.js");
load("browser-saving-throws.js");

const action = {
  id: "enlarge", name: "Enlarge", actionCost: "action",
  resourceId: "enlarge", resourceCost: 1, durationRounds: 10,
  expiryTiming: "source_turn_end", openingEligible: false,
  conditionIds: [], magicalEffect: true, sizeOverride: "large",
  abilityCheckAdvantageAbilities: ["strength"],
  savingThrowAdvantageGrants: [{
    source_id: "enlarge-strength-save", source_name: "Enlarge",
    abilities: ["strength"],
  }],
};
const base = {
  id: "shared-medium", name: "Renamed creature", size: "medium", max_hp: 26,
  armor_class: 16, ability_scores: { strength: 14, dexterity: 11 },
  saving_throw_bonuses: { strength: 2, dexterity: 0 },
  timed_self_buff_actions: [action], innate_condition_ids: [],
  condition_immunities: [], damage_resistances: [],
};
const state = {
  template: base, current_hp: 26, is_alive: true, is_dead: false,
  is_unconscious: false, active_effect_ids: [], timed_effects: [],
  active_modifiers: [], resources: { enlarge: 1 },
  action_available: true, bonus_action_available: true, reaction_available: true,
  temporary_damage_resistances: [],
};
const member = { combatant_id: "owner", side: "monsters", state };
const war = {
  id: "war", name: "War Pick", weaponId: "war", kind: "melee",
  diceCount: 1, diceSize: 8, damageBonus: 2, damageType: "piercing",
  conditionalDamage: {
    trigger: "attacker_effect_active", requiredEffectId: "enlarge",
    mode: "replace_weapon", diceCount: 2, diceSize: 8,
    damageBonus: 2, damageType: "piercing",
  },
};
function rollDice(values) {
  const pending = [...values];
  window.IRON_PIT_DICE = {
    roll: (sides) => {
      const value = pending.shift();
      assert.ok(value > 0 && value <= sides, "unexpected dice request");
      return value;
    },
    rollMany: (count, sides) => Array.from(
      { length: count }, () => window.IRON_PIT_DICE.roll(sides),
    ),
  };
  return pending;
}
try {
  assert.equal(window.IRON_PIT_BROWSER_STATE.effectiveSize(state), "medium");
  let pending = rollDice([4]);
  const unbuffed = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(state, war, false, "normal", "1");
  assert.equal(unbuffed.roll.total, 6);
  assert.equal(pending.length, 0);

  window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS.resolve(
    1, 1, member, action, { spendActionCost: false, affectedStates: [state] },
  );
  assert.equal(state.resources.enlarge, 0);
  assert.equal(window.IRON_PIT_BROWSER_STATE.effectiveSize(state), "large");
  assert.equal(window.IRON_PIT_BROWSER_STATE.sizeAtMost(member, "medium"), false);
  assert.equal(window.IRON_PIT_BROWSER_STATE.timedCheckAdvantage(state, "strength"), 1);
  assert.equal(window.IRON_PIT_BROWSER_STATE.timedCheckAdvantage(state, "dexterity"), 0);
  assert.equal(window.IRON_PIT_BROWSER_ABILITY_CHECKS.mode(
    state, 0, 0, { ability: "strength" },
  ), "advantage");

  pending = rollDice([4, 5]);
  const enlarged = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(state, war, false, "normal", "2");
  assert.equal(enlarged.roll.total, 11);
  assert.equal(enlarged.roll.notation, "2d8+2");
  assert.equal(pending.length, 0);
  pending = rollDice([3, 17]);
  assert.equal(window.IRON_PIT_BROWSER_SAVING_THROWS.resolveSavingThrow(
    state, "strength", 99,
  ).roll.mode, "advantage");
  assert.equal(pending.length, 0);

  window.IRON_PIT_BROWSER_TIMED.removeGroup(
    state, state.timed_effects.find((effect) => effect.source_effect_id === "enlarge"),
  );
  assert.equal(window.IRON_PIT_BROWSER_STATE.effectiveSize(state), "medium");
  assert.equal(window.IRON_PIT_BROWSER_STATE.timedCheckAdvantage(state, "strength"), 0);
  pending = rollDice([4]);
  assert.equal(window.IRON_PIT_BROWSER_ROLLS.weaponDamage(
    state, war, false, "normal", "3",
  ).roll.total, 6);
  assert.equal(pending.length, 0);
} catch (error) {
  console.error("Source-neutral Enlarge runtime regression failed", error);
  throw error;
}
console.log("2014 source Enlarge universal browser parity passed.");
