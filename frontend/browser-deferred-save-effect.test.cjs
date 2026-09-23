"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (file) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, file), "utf8"),
  { filename: file },
);

load("browser-ability-hooks.js");
load("browser-attack-outcome.js");

window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "action" && state.action_available && !state.is_dead && !state.is_unconscious,
  spend: (state, cost) => {
    assert.equal(cost, "action");
    if (!state.action_available) throw new Error("action is unavailable");
    state.action_available = false;
  },
};
window.IRON_PIT_BROWSER_RESOURCES = {
  available: (state, id, cost = 1) => (state.resources[id] || 0) >= cost,
  spend: (state, id, cost = 1) => {
    if ((state.resources[id] || 0) < cost) throw new Error("resource is unavailable");
    state.resources[id] -= cost;
  },
};
window.IRON_PIT_BROWSER_CONCENTRATION = { endIfIncapacitated: () => false };

let saveResult = { roll: { total: 1, selected_roll: 1 }, succeeded: false };
window.IRON_PIT_BROWSER_SAVES = {
  resolveSavingThrow: () => saveResult,
};

let diceValues = [];
window.IRON_PIT_DICE = { roll: () => diceValues.shift() };

let reduceCalls = 0;
window.IRON_PIT_BROWSER_ZERO_HP = {
  reduceToZeroHitPoints: (state) => {
    reduceCalls += 1;
    state.current_hp = 0;
    state.is_alive = false;
    state.is_dead = true;
    state.is_unconscious = false;
    return "dead";
  },
};

window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage: (_state, amount, type) => {
    assert.equal(type, "necrotic");
    return amount;
  },
  applyDamage: (state, amount) => {
    state.current_hp = Math.max(0, state.current_hp - amount);
    return state.current_hp === 0 ? "dead" : "damaged";
  },
};

load("browser-deferred-save-effect.js");

const H = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
const D = window.IRON_PIT_BROWSER_DEFERRED_SAVE_EFFECT;
const rule = {
  source_id: "quivering-palm",
  source_name: "Quivering Palm",
  trigger_attack_ids: ["unarmed-strike"],
  resource_id: "ki",
  resource_cost: 3,
  save_ability: "constitution",
  save_dc: 18,
  failure_sets_zero_hp: true,
  success_damage_dice_count: 10,
  success_damage_dice_size: 10,
  success_damage_type: "necrotic",
};

function actor() {
  return {
    combatant_id: "hero-1:monk",
    state: {
      template: { id: "monk", name: "Kael", ruleset: "2014", deferred_save_effect: { ...rule } },
      resources: { ki: 17 },
      deferred_effects: [],
      action_available: true,
      is_dead: false,
      is_unconscious: false,
      is_alive: true,
    },
  };
}

function target(id = "monster-1:target") {
  return {
    combatant_id: id,
    state: {
      template: { id, name: "Target", ruleset: "2014" },
      current_hp: 100,
      temporary_hp: 0,
      death_save_successes: 0,
      death_save_failures: 0,
      is_alive: true,
      is_dead: false,
      is_unconscious: false,
      is_stable: false,
    },
  };
}

{
  const member = actor(), victim = target();
  const setup = { heroes: [member], monsters: [victim] };
  const attackOutcome = {};
  const hook = H.runPhase(H.PHASES.ON_HIT, {
    sequence: 1,
    round: 1,
    member,
    target: victim,
    originalTarget: victim,
    attack: { id: "unarmed-strike" },
    setup,
    attackOutcome,
    events: [],
  });

  assert.deepEqual(hook.events, []);
  assert.equal(member.state.resources.ki, 14);
  assert.deepEqual(member.state.deferred_effects, [
    { source_id: "quivering-palm", target_id: victim.combatant_id },
  ]);
  assert.equal(attackOutcome.deferredEffectArmed, "Quivering Palm");

  const snapshot = JSON.stringify(member.state);
  assert.equal(D.candidate(member, setup), victim);
  assert.equal(JSON.stringify(member.state), snapshot, "candidate discovery must be side-effect free");

  const second = target("monster-2:other");
  setup.monsters.push(second);
  H.runPhase(H.PHASES.ON_HIT, {
    sequence: 2, round: 1, member, target: second, originalTarget: second,
    attack: { id: "unarmed-strike" }, setup, attackOutcome: {}, events: [],
  });
  assert.equal(member.state.resources.ki, 14);
  assert.equal(member.state.deferred_effects.length, 1);
  assert.equal(member.state.deferred_effects[0].target_id, victim.combatant_id);
}

{
  reduceCalls = 0;
  const member = actor(), victim = target(), setup = { heroes: [member], monsters: [victim] };
  member.state.resources.ki = 14;
  member.state.deferred_effects.push({ source_id: "quivering-palm", target_id: victim.combatant_id });
  saveResult = { roll: { total: 5, selected_roll: 1 }, succeeded: false };

  const event = D.resolve(3, 2, member, setup, victim.combatant_id);
  assert.equal(reduceCalls, 1);
  assert.equal(victim.state.current_hp, 0);
  assert.equal(victim.state.is_dead, true);
  assert.equal(member.state.action_available, false);
  assert.deepEqual(member.state.deferred_effects, []);
  assert.equal(event.feature_id, "quivering-palm");
  assert.match(event.description, /Quivering Palm/);
}

{
  const member = actor(), victim = target(), setup = { heroes: [member], monsters: [victim] };
  member.state.resources.ki = 14;
  member.state.deferred_effects.push({ source_id: "quivering-palm", target_id: victim.combatant_id });
  saveResult = { roll: { total: 24, selected_roll: 20 }, succeeded: true };
  diceValues = Array(10).fill(5);

  const event = D.resolve(4, 3, member, setup, victim.combatant_id);
  assert.equal(event.save_succeeded, true);
  assert.equal(event.damage_roll.notation, "10d10");
  assert.equal(event.damage_roll.total, 50);
  assert.equal(event.damage_components[0].source, "Quivering Palm");
  assert.equal(event.damage_components[0].damage_type, "necrotic");
  assert.equal(victim.state.current_hp, 50);
  assert.equal(member.state.action_available, false);
  assert.deepEqual(member.state.deferred_effects, []);
}

console.log("Browser deferred save effect supports source-tagged arming, one live mark, Action activation, zero-HP failure, and typed success damage.");
