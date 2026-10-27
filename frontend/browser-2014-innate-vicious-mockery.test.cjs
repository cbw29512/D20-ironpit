"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_DEBUFF_COUNTERS = { movementCost: () => null };
load("browser-timed-conditions.js");
load("browser-failed-save-timed-effects.js");
window.IRON_PIT_BROWSER_SAVING_THROWS = {
  resolveSavingThrow: () => ({ roll: { rolls: [1], total: 1 }, succeeded: false }),
  saveMode: () => "normal",
};
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "action" && state.action_available,
  spend: (state) => { state.action_available = false; },
};
window.IRON_PIT_BROWSER_STATE = { sizeAtMost: () => true };
window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS = { saveAdvantageSourceNames: () => [] };
window.IRON_PIT_BROWSER_CONDITION_RULES = { canSee: () => true };
window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES = {
  resolveDamage: (_state, amount) => ({ applied: amount, healed: 0, sourceName: null }),
};
window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage: (_state, amount) => amount,
  applyDamage: (state, amount) => { state.current_hp -= amount; },
};
window.IRON_PIT_BROWSER_GRAPPLE = { apply: () => [] };
window.IRON_PIT_DICE = { rollMany: () => [4] };
for (const file of [
  "browser-save-immunity.js", "browser-save-action-support.js", "browser-save-action-attempt.js",
  "browser-save-damage.js", "browser-save-damage-legacy.js", "browser-save-damage-apply.js",
  "browser-save-action-effects.js", "browser-save-event.js", "browser-saves.js",
]) load(file);

function combatant(id, side) {
  return {
    combatant_id: id, side,
    state: {
      template: { name: id, creature_type: "humanoid" }, current_hp: 20,
      temporary_hp: 0, is_alive: true, is_dead: false, is_stable: false,
      death_save_successes: 0, death_save_failures: 0, active_effect_ids: [],
      timed_effects: [], active_modifiers: [], action_available: true,
      current_round: 1, resources: {},
    },
  };
}

const source = combatant("green-hag", "monsters");
const target = combatant("target", "heroes");
const action = {
  id: "vicious-mockery", name: "Vicious Mockery", actionCost: "action",
  level: 0, range: 60, requiresTargetSight: true, requiresTargetHearing: true,
  saveAbility: "wisdom", dc: 12, damageDiceCount: 1, damageDiceSize: 4,
  damageBonus: 0, damageType: "psychic", successDamage: "none",
  failedSaveTimedEffect: {
    effectId: "vicious-mockery-disadvantage", expiryTiming: "target_turn_end",
    nextAttackDisadvantage: true,
  },
};
const immutableAction = JSON.stringify(action);
const event = window.IRON_PIT_BROWSER_SAVES.resolveAction(1, 1, source, target, action, 30);
assert.equal(event.save_succeeded, false);
assert.equal(event.damage_roll.total, 4);
assert.equal(target.state.current_hp, 16);
assert.equal(source.state.action_available, false);
const effect = target.state.timed_effects.find(
  (item) => item.effect_id === "vicious-mockery-disadvantage",
);
assert.ok(effect);
assert.equal(effect.expiry_timing, "target_turn_end");
assert.equal(effect.next_attack_disadvantage, true);
assert.equal(JSON.stringify(action), immutableAction);

console.log("2014 innate Vicious Mockery damage and next-attack-disadvantage browser parity passed.");
