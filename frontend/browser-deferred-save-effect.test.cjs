"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

let saveResult = { roll: { total: 1 }, succeeded: false };
let diceValues = [];
window.IRON_PIT_DICE = { roll: () => diceValues.length ? diceValues.shift() : 1 };
window.IRON_PIT_BROWSER_SAVES = { resolveSavingThrow: () => saveResult };
window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage: (target, amount, type) =>
    target.template.damage_resistances?.includes(type) ? Math.floor(amount / 2) : amount,
  applyDamage: (target, amount) => {
    target.current_hp = Math.max(0, target.current_hp - amount);
    return target.current_hp === 0 ? "unconscious" : "damaged";
  },
};
window.IRON_PIT_BROWSER_ZERO_HP = {
  reduceToZero: (target) => {
    target.current_hp = 0;
    target.is_unconscious = true;
    return "unconscious";
  },
};

load("browser-action-economy.js");
load("browser-ability-hooks.js");
load("browser-attack-outcome.js");
load("browser-deferred-save-effect.js");
window.IRON_PIT_BROWSER_DEFERRED_SAVE_EFFECT.installAbilityHooks();

const H = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
const O = window.IRON_PIT_BROWSER_ATTACK_OUTCOME;
const D = window.IRON_PIT_BROWSER_DEFERRED_SAVE_EFFECT;

const rule = {
  source_id: "quivering-palm",
  source_name: "Quivering Palm",
  trigger_weapon_ids: ["unarmed-strike"],
  resource_id: "ki",
  resource_cost: 3,
  save_ability: "constitution",
  save_dc: 18,
  failure_sets_zero_hp: true,
  success_damage_dice_count: 10,
  success_damage_dice_size: 10,
  success_damage_type: "necrotic",
  max_active_targets: 1,
};

function state(name, { resistance = false } = {}) {
  return {
    template: {
      name,
      ruleset: "2014",
      deferred_save_effect: name === "Kael" ? rule : null,
      damage_resistances: resistance ? ["necrotic"] : [],
    },
    current_hp: 200,
    temporary_hp: 0,
    is_alive: true,
    is_dead: false,
    is_unconscious: false,
    is_stable: false,
    death_save_successes: 0,
    death_save_failures: 0,
    action_available: true,
    bonus_action_available: true,
    reaction_available: true,
    resources: name === "Kael" ? { ki: 17 } : {},
    deferred_effects: [],
  };
}

function pair({ resistance = false } = {}) {
  const actor = { combatant_id: "hero-kael", side: "heroes", state: state("Kael") };
  const target = { combatant_id: "monster-target", side: "monsters", state: state("Target", { resistance }) };
  return { actor, target, setup: { heroes: [actor], monsters: [target] } };
}

{
  const { actor, target, setup } = pair();
  const outcome = O.create();
  const result = H.runPhase(H.PHASES.ON_HIT, {
    sequence: 4,
    round: 1,
    member: actor,
    target,
    originalTarget: target,
    attack: { id: "kael-unarmed", weaponId: "unarmed-strike" },
    setup,
    attackOutcome: outcome,
    events: [],
  });
  assert.deepEqual(result.events, []);
  assert.equal(outcome.deferredEffectArmed.sourceName, "Quivering Palm");
  assert.equal(outcome.deferredEffectArmed.resourceRemaining, 14);
  assert.equal(actor.state.resources.ki, 14);
  assert.deepEqual(actor.state.deferred_effects, [
    { source_id: "quivering-palm", target_id: target.combatant_id, armed_round: 1 },
  ]);

  const duplicate = O.create();
  H.runPhase(H.PHASES.ON_HIT, {
    sequence: 5,
    round: 1,
    member: actor,
    target,
    originalTarget: target,
    attack: { id: "kael-unarmed", weaponId: "unarmed-strike" },
    setup,
    attackOutcome: duplicate,
    events: [],
  });
  assert.equal(duplicate.deferredEffectArmed, null);
  assert.equal(actor.state.resources.ki, 14);

  actor.state.action_available = false;
  assert.equal(D.candidate(actor, setup), null);
  actor.state.action_available = true;
  saveResult = { roll: { total: 3 }, succeeded: false };
  const event = D.resolve(6, 2, actor, setup, target.combatant_id);
  assert.equal(event.feature_id, "quivering-palm");
  assert.match(event.description, /Quivering Palm/);
  assert.equal(event.save_succeeded, false);
  assert.equal(target.state.current_hp, 0);
  assert.equal(target.state.is_unconscious, true);
  assert.equal(actor.state.action_available, false);
  assert.deepEqual(actor.state.deferred_effects, []);
}

{
  const { actor, target, setup } = pair({ resistance: true });
  const outcome = O.create();
  H.runPhase(H.PHASES.ON_HIT, {
    sequence: 1,
    round: 1,
    member: actor,
    target,
    originalTarget: target,
    attack: { id: "kael-unarmed", weaponId: "unarmed-strike" },
    setup,
    attackOutcome: outcome,
    events: [],
  });
  saveResult = { roll: { total: 22 }, succeeded: true };
  diceValues = Array(10).fill(1);
  const before = target.state.current_hp;
  const event = D.resolve(2, 2, actor, setup, target.combatant_id);
  assert.equal(event.save_succeeded, true);
  assert.equal(event.damage_roll.total, 5);
  assert.equal(event.damage_components[0].source, "Quivering Palm");
  assert.equal(event.damage_components[0].total, 10);
  assert.equal(event.damage_components[0].applied_total, 5);
  assert.equal(target.state.current_hp, before - 5);
  assert.deepEqual(actor.state.deferred_effects, []);
}

{
  const { actor, target, setup } = pair();
  actor.state.deferred_effects.push({
    source_id: "quivering-palm",
    target_id: target.combatant_id,
    armed_round: 1,
  });
  const before = JSON.stringify(actor.state.deferred_effects);
  assert.equal(D.candidate(actor, setup), target);
  assert.equal(JSON.stringify(actor.state.deferred_effects), before, "candidate discovery must be side-effect free");

  target.state.current_hp = 0;
  target.state.is_unconscious = true;
  assert.equal(D.candidate(actor, setup), null);
  assert.equal(JSON.stringify(actor.state.deferred_effects), before, "dead-target discovery must still be read-only");

  D.cleanup(setup);
  assert.deepEqual(actor.state.deferred_effects, []);
}

console.log("Browser universal deferred save-effect regressions passed.");
