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
window.IRON_PIT_BROWSER_CONDITION_RULES = {
  has: (state, id) => state.active_effect_ids.includes(id),
  canSee: () => true,
  incapacitated: (state) => state.active_effect_ids.includes("incapacitated"),
};
load("browser-timed-conditions.js");
load("browser-failed-save-timed-effects.js");
load("browser-source-bound-effects.js");
window.IRON_PIT_BROWSER_SAVING_THROWS = {
  resolveSavingThrow: () => ({ roll: 1, succeeded: false }),
  saveMode: () => "normal",
};
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "action" && state.action_available,
  spend: (state) => { state.action_available = false; },
};
window.IRON_PIT_BROWSER_STATE = { sizeAtMost: () => true, distance: () => 5 };
window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS = { saveAdvantageSourceNames: () => [] };
window.IRON_PIT_BROWSER_ATTACK = { applyDamage: () => null };
window.IRON_PIT_BROWSER_GRAPPLE = { apply: () => [] };
window.IRON_PIT_DICE = { rollMany: () => [] };
load("browser-saves.js");

function member(id, side, type = "monstrosity") {
  return {
    combatant_id: id,
    side,
    state: {
      template: { name: id, creature_type: type, innate_condition_ids: [] },
      current_hp: 20,
      temporary_hp: 0,
      is_alive: true,
      is_dead: false,
      is_stable: false,
      death_save_successes: 0,
      death_save_failures: 0,
      active_effect_ids: [],
      timed_effects: [],
      active_modifiers: [],
      action_available: true,
      bonus_action_available: true,
      turns_started: 0,
      current_round: 1,
      resources: {},
    },
  };
}

const first = member("first-source", "monsters");
const second = member("second-source", "monsters");
const target = member("target", "heroes", "humanoid");
const setup = { heroes: [target], monsters: [first, second] };
const action = {
  id: "renamed-maintained-control",
  name: "Source Label Only",
  actionCost: "action",
  saveAbility: "wisdom",
  dc: 11,
  range: 300,
  requiresTargetHearing: true,
  requiredTargetCreatureTypes: ["humanoid", "giant"],
  prohibitedTargetSourceEffectIds: ["renamed-maintained-control"],
  magicalEffect: true,
  failedSaveTimedEffect: {
    effectId: "charmed",
    additionalEffectIds: ["incapacitated"],
    repeatSaveAbility: "wisdom",
    repeatSaveDc: 11,
    repeatSaveTiming: "target_turn_end",
    sourceMaintenanceActionCost: "bonus_action",
    turnBehavior: "forced_approach_source",
    endsIfSourceIncapacitated: true,
    endsIfSourceDead: true,
    sourceEffectImmunityOnEnd: true,
  },
};
const before = JSON.stringify(action);
window.IRON_PIT_BROWSER_SAVES.resolveAction(
  1, 1, first, target, action, 5, { setup },
);
assert.deepEqual(target.state.active_effect_ids.sort(), ["charmed", "incapacitated"]);
assert.equal(
  window.IRON_PIT_BROWSER_SAVES.legalAction(
    action, target, 5, second.combatant_id, second,
  ),
  false,
);

first.state.is_dead = true;
first.state.is_alive = false;
first.state.current_hp = 0;
window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS.cleanupDisabledSources(setup);
assert.deepEqual(target.state.active_effect_ids, []);
assert.equal(
  target.state.timed_effects.some((effect) =>
    String(effect.effect_id).includes(":success-immunity:")),
  false,
);
assert.equal(
  window.IRON_PIT_BROWSER_SAVES.legalAction(
    action, target, 5, second.combatant_id, second,
  ),
  true,
);
assert.equal(JSON.stringify(action), before);
console.log("Browser maintained audible control eligibility and cleanup passed.");
