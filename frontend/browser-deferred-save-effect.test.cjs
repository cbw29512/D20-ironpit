"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "action" && state.action_available,
  spend: (state, cost) => { if (cost === "action") state.action_available = false; },
};
window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage: (_state, amount, type) => type === "necrotic" ? amount : amount,
  applyDamage: (state, amount) => { state.current_hp = Math.max(0, state.current_hp - amount); },
};
window.IRON_PIT_BROWSER_ZERO_HP = {
  reduceToZero: (state) => {
    state.current_hp = 0; state.is_alive = true; state.is_unconscious = true; state.is_dead = false;
    return "unconscious";
  },
};
let saveResult = { roll: { total: 1 }, succeeded: false };
window.IRON_PIT_BROWSER_SAVES = { resolveSavingThrow: () => saveResult };
let dice = [];
window.IRON_PIT_DICE = { roll: () => {
  const value = dice.shift();
  if (value == null) throw new Error("No test die remains.");
  return value;
} };

load("browser-deferred-save-effect.js");

function member(id, side, hp, rule = null, resources = {}) {
  return {
    combatant_id: id, side, position_ft: 0,
    state: {
      template: { name: id, deferred_save_effect: rule },
      current_hp: hp, temporary_hp: 0, is_alive: true, is_dead: false, is_unconscious: false,
      death_save_successes: 0, death_save_failures: 0,
      action_available: true, resources: { ...resources }, deferred_effects: [],
    },
  };
}

const rule = {
  source_id: "test-deferred",
  trigger_attack_ids: ["unarmed-strike"],
  resource_id: "ki", resource_cost: 3,
  save_ability: "constitution", save_dc: 18,
  failure_sets_zero_hp: true,
  success_damage_dice_count: 10, success_damage_dice_size: 10,
  success_damage_type: "necrotic",
};

{
  const actor = member("actor", "heroes", 100, rule, { ki: 17 });
  const target = member("target", "monsters", 100);
  const setup = { heroes: [actor], monsters: [target] };

  assert.equal(window.IRON_PIT_BROWSER_DEFERRED_SAVE_EFFECT.arm(actor.state, target.combatant_id, "unarmed-strike"), "test-deferred");
  assert.equal(actor.state.resources.ki, 14);
  assert.deepEqual(actor.state.deferred_effects, [{ source_id: "test-deferred", target_id: "target" }]);
  assert.equal(window.IRON_PIT_BROWSER_DEFERRED_SAVE_EFFECT.arm(actor.state, "other", "unarmed-strike"), null);
  assert.equal(actor.state.resources.ki, 14);

  saveResult = { roll: { total: 1 }, succeeded: false };
  const event = window.IRON_PIT_BROWSER_DEFERRED_SAVE_EFFECT.resolve(1, 2, actor, setup, "target");
  assert.equal(event.feature_id, "test-deferred");
  assert.equal(event.save_succeeded, false);
  assert.equal(target.state.current_hp, 0);
  assert.equal(target.state.is_unconscious, true);
  assert.equal(actor.state.action_available, false);
  assert.deepEqual(actor.state.deferred_effects, []);
}

{
  const actor = member("actor2", "heroes", 100, rule, { ki: 17 });
  const target = member("target2", "monsters", 100);
  const setup = { heroes: [actor], monsters: [target] };
  assert.equal(window.IRON_PIT_BROWSER_DEFERRED_SAVE_EFFECT.arm(actor.state, target.combatant_id, "unarmed-strike"), "test-deferred");
  saveResult = { roll: { total: 25 }, succeeded: true };
  dice = Array(10).fill(5);
  const event = window.IRON_PIT_BROWSER_DEFERRED_SAVE_EFFECT.resolve(2, 2, actor, setup, "target2");
  assert.equal(event.save_succeeded, true);
  assert.equal(event.damage_roll.total, 50);
  assert.equal(target.state.current_hp, 50);
  assert.deepEqual(actor.state.deferred_effects, []);
}

console.log("Universal browser deferred-save effect supports mark, activate, zero-HP, and damage paths.");
