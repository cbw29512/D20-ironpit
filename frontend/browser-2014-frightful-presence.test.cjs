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
window.IRON_PIT_BROWSER_CONDITION_RULES = { incapacitated: () => false, autoFailStrDex: () => false };
window.IRON_PIT_BROWSER_ATTACK = { adjustedDamage: (_state, amount) => amount, applyDamage: () => null };
window.IRON_PIT_BROWSER_GRAPPLE = { apply: () => [] };
window.IRON_PIT_BROWSER_BARBARIAN2 = { dangerSenseAdvantage: () => 0 };
window.IRON_PIT_BROWSER_DODGE = { dexSaveAdvantageSources: () => 0 };
window.IRON_PIT_BROWSER_MODIFIERS = {
  applyD20Bonus: (_state, _kind, roll) => roll,
  expireTargetTurn: () => {},
};
window.IRON_PIT_BROWSER_CONCENTRATION = { endIfIncapacitated: () => {} };
window.IRON_PIT_BROWSER_STATE = { sizeAtMost: () => true };

load("browser-source-effect-immunity.js");
load("browser-action-economy.js");
load("browser-timed-conditions.js");
load("browser-save-control-effects.js");
load("browser-rolls.js");
load("browser-saves.js");
load("browser-grid-geometry.js");
load("browser-area-shapes.js");
load("browser-area-targeting.js");
load("browser-area-save-actions.js");
load("browser-condition-lifecycle.js");

function dice(values) {
  const queue = [...values];
  window.IRON_PIT_DICE = {
    roll: () => {
      if (!queue.length) throw new Error("unexpected die roll");
      return queue.shift();
    },
    rollMany: (count) => Array.from({ length: count }, () => {
      if (!queue.length) throw new Error("unexpected die roll");
      return queue.shift();
    }),
  };
}

function member(id, side, x, y) {
  return {
    combatant_id: id,
    side,
    position_ft: x * 5,
    state: {
      position: { x, y }, action_available: true, bonus_action_available: true,
      reaction_available: true, turn_terminated: false, is_alive: true, is_dead: false,
      is_unconscious: false, is_stable: false, current_hp: 50, temporary_hp: 0,
      death_save_successes: 0, death_save_failures: 0, active_effect_ids: [],
      grapple_sources: [], timed_effects: [], resources: {}, concentration: null,
      source_effect_immunities: [],
      template: {
        name: id, size: "medium", ruleset: "2014", traits: [],
        saving_throw_bonuses: { wisdom: 0 }, resource_definitions: [], saving_throw_actions: [],
      },
    },
  };
}

const action = {
  id: "frightful-presence", name: "Frightful Presence", saveAbility: "wisdom", dc: 19,
  range: 120, area: { shape: "emanation", origin: "self", radius_ft: 120 },
  damageDiceCount: 0, damageDiceSize: 6, damageBonus: 0, damageType: null,
  successDamage: "none",
  failureControlEffect: {
    conditionId: "frightened", expiryTiming: "target_turn_end", durationRounds: 10,
    repeatSaveAbility: "wisdom", repeatSaveDc: 19, repeatSaveTiming: "target_turn_end",
    sourceEffectImmunityOnEnd: true,
  },
  sourceEffectImmunityOnSuccess: true, animation: "fear",
};

const actor = member("monster-1:dragon", "monsters", 1, 1);
const target = member("hero-1:target", "heroes", 4, 1);
actor.state.template.saving_throw_actions = [action];
const setup = {
  heroes: [target], monsters: [actor],
  map_definition: { id: "fear-test", width_squares: 30, height_squares: 30, cell_size_ft: 5 },
};

dice([1]);
const failed = window.IRON_PIT_BROWSER_AREA_SAVES.resolve(1, 1, actor, setup, false);
assert.ok(failed);
assert.equal(failed.events[0].save_succeeded, false);
assert.equal(target.state.active_effect_ids.includes("frightened"), true);
assert.equal(target.state.timed_effects[0].expires_round, 11);

actor.state.action_available = true;
dice([20]);
const repeat = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(
  2, 2, target, "target_turn_end",
);
assert.equal(repeat.events[0].save_succeeded, true);
assert.equal(target.state.active_effect_ids.includes("frightened"), false);
assert.equal(
  window.IRON_PIT_BROWSER_SOURCE_EFFECT_IMMUNITY.immune(
    target.state, actor.combatant_id, action.id,
  ),
  true,
);

const noEligibleTargets = window.IRON_PIT_BROWSER_AREA_SAVES.choice(actor, setup, false);
assert.equal(noEligibleTargets, null);

const fresh = member("hero-2:fresh", "heroes", 5, 1);
const freshSetup = { ...setup, heroes: [fresh] };
actor.state.action_available = true;
dice([20]);
const succeeded = window.IRON_PIT_BROWSER_AREA_SAVES.resolve(3, 3, actor, freshSetup, false);
assert.equal(succeeded.events[0].save_succeeded, true);
assert.equal(
  window.IRON_PIT_BROWSER_SOURCE_EFFECT_IMMUNITY.immune(
    fresh.state, actor.combatant_id, action.id,
  ),
  true,
);

console.log("2014 browser Frightful Presence regressions passed.");
