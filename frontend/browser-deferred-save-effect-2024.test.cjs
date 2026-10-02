"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

let saveSucceeded = false;
let diceValues = [];
window.IRON_PIT_DICE = { roll: () => diceValues.shift() ?? 1 };
window.IRON_PIT_BROWSER_SAVES = {
  resolveSavingThrow: () => ({ roll: { total: saveSucceeded ? 20 : 1 }, succeeded: saveSucceeded }),
};
window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage: (_state, amount) => amount,
  applyDamage: (state, amount) => { state.current_hp = Math.max(0, state.current_hp - amount); },
};
window.IRON_PIT_BROWSER_ZERO_HP = { reduceToZero: (state) => { state.current_hp = 0; } };

load("browser-action-economy.js");
load("browser-deferred-save-effect-outcomes.js");
load("browser-deferred-save-effect.js");
load("browser-deferred-save-effect-attack-slot.js");

const DE = window.IRON_PIT_BROWSER_DEFERRED_SAVE_EFFECT;
const SLOT = window.IRON_PIT_BROWSER_DEFERRED_ATTACK_SLOT;

const rule = {
  source_id: "test-deferred",
  source_name: "Test Deferred",
  trigger_weapon_ids: ["unarmed-strike"],
  resource_id: "focus",
  resource_cost: 4,
  save_ability: "constitution",
  save_dc: 16,
  failure_sets_zero_hp: false,
  failure_damage_dice_count: 10,
  failure_damage_dice_size: 12,
  failure_damage_type: "force",
  success_damage_from_failure: "half",
  success_damage_dice_count: 0,
  success_damage_dice_size: 10,
  success_damage_type: null,
  allow_attack_slot_activation: true,
  allow_harmless_end_on_rearm: true,
  max_active_targets: 1,
};

function state(name, source = false) {
  return {
    template: { name, deferred_save_effect: source ? rule : null, damage_resistances: [] },
    current_hp: 300,
    temporary_hp: 0,
    is_alive: true,
    is_dead: false,
    is_unconscious: false,
    is_stable: false,
    death_save_successes: 0,
    death_save_failures: 0,
    action_available: false,
    bonus_action_available: true,
    reaction_available: true,
    resources: source ? { focus: 17 } : {},
    deferred_effects: [],
  };
}

function fixture() {
  const actor = { combatant_id: "hero", side: "heroes", state: state("Source", true) };
  const first = { combatant_id: "first", side: "monsters", state: state("First") };
  const second = { combatant_id: "second", side: "monsters", state: state("Second") };
  return { actor, first, second, setup: { heroes: [actor], monsters: [first, second] } };
}

{
  const { actor, first, setup } = fixture();
  const armed = DE.arm(actor.state, first.state, first.combatant_id, { weaponId: "unarmed-strike" }, 1);
  assert.equal(armed.resourceRemaining, 13);
  saveSucceeded = false;
  diceValues = Array(10).fill(12);
  const event = SLOT.resolve(1, 1, actor, setup);
  assert.ok(event);
  assert.equal(event.damage_roll.total, 120);
  assert.equal(event.damage_components[0].damage_type, "force");
  assert.equal(first.state.current_hp, 180);
  assert.equal(actor.state.action_available, false);
}

{
  const { actor, first, setup } = fixture();
  DE.arm(actor.state, first.state, first.combatant_id, { weaponId: "unarmed-strike" }, 1);
  saveSucceeded = true;
  diceValues = Array(10).fill(12);
  const event = SLOT.resolve(1, 1, actor, setup);
  assert.equal(event.damage_roll.total, 60);
  assert.equal(first.state.current_hp, 240);
}

{
  const { actor, first, second } = fixture();
  DE.arm(actor.state, first.state, first.combatant_id, { weaponId: "unarmed-strike" }, 1);
  assert.equal(DE.arm(actor.state, first.state, first.combatant_id, { weaponId: "unarmed-strike" }, 1), null);
  assert.equal(actor.state.resources.focus, 13);

  const replacement = DE.arm(actor.state, second.state, second.combatant_id, { weaponId: "unarmed-strike" }, 1);
  assert.equal(replacement.resourceRemaining, 9);
  assert.deepEqual(actor.state.deferred_effects, [
    { source_id: "test-deferred", target_id: second.combatant_id, armed_round: 1 },
  ]);
}

console.log("Browser deferred save-effect 2024 extension regressions passed.");
