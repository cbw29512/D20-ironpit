"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_DEBUFF_COUNTERS = { movementCost: () => null };
load("browser-timed-conditions.js");
load("browser-failed-save-timed-effects.js");
window.IRON_PIT_BROWSER_SAVING_THROWS = {
  resolveSavingThrow: (_state, _ability, dc) => ({
    roll: window.__saveRoll,
    succeeded: window.__saveRoll >= dc,
  }),
  saveMode: () => "normal",
};
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "action" && state.action_available,
  spend: (state) => { state.action_available = false; },
};
window.IRON_PIT_BROWSER_STATE = { sizeAtMost: () => true };
window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS = { saveAdvantageSourceNames: () => [] };
window.IRON_PIT_BROWSER_CONDITION_RULES = { canSee: () => true };
window.IRON_PIT_BROWSER_ATTACK = { adjustedDamage: (_state, amount) => amount, applyDamage: () => null };
window.IRON_PIT_BROWSER_GRAPPLE = { apply: () => [] };
window.IRON_PIT_DICE = { rollMany: () => [] };
load("browser-saves.js");
load("browser-condition-lifecycle.js");

function combatant(id, name, side) {
  return {
    combatant_id: id,
    side,
    state: {
      template: { name, creature_type: "humanoid" },
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
      current_round: 1,
      resources: {},
    },
  };
}

const action = {
  id: "frightful-presence",
  name: "Frightful Presence",
  actionCost: "action",
  saveAbility: "wisdom",
  dc: 16,
  range: 120,
  sourceEffectImmunityOnSuccess: true,
  failedSaveTimedEffect: {
    effectId: "frightened",
    durationRounds: 10,
    expiryTiming: "target_turn_end",
    repeatSaveAbility: "wisdom",
    repeatSaveDc: 16,
    repeatSaveTiming: "target_turn_end",
    sourceEffectImmunityOnEnd: true,
  },
  animation: "fear",
};

function setupPair() {
  const dragon = combatant("dragon-1", "Adult Black Dragon", "monsters");
  const hero = combatant("hero-1", "Karnok Stoneward", "heroes");
  dragon.state.template.name = "Adult Black Dragon";
  return { dragon, hero };
}

window.__saveRoll = 1;
let { dragon, hero } = setupPair();
let event = window.IRON_PIT_BROWSER_SAVES.resolveAction(1, 1, dragon, hero, action, 10);
assert.equal(event.save_succeeded, false);
assert.deepEqual(event.applied_condition_ids, ["frightened"]);
assert.ok(hero.state.active_effect_ids.includes("frightened"));
assert.match(event.description, /Frightful Presence/);
assert.equal(event.feature_id, "frightful-presence");

({ dragon, hero } = setupPair());
window.__saveRoll = 20;
event = window.IRON_PIT_BROWSER_SAVES.resolveAction(1, 1, dragon, hero, action, 10);
assert.equal(event.save_succeeded, true);
assert.ok(!hero.state.active_effect_ids.includes("frightened"));
assert.match(event.description, /Frightful Presence/);
assert.equal(
  window.IRON_PIT_BROWSER_FAILED_SAVE_TIMED_EFFECTS.isImmune(hero, action, dragon.combatant_id),
  true,
);
assert.equal(window.IRON_PIT_BROWSER_SAVES.legalAction(action, hero, 10, dragon.combatant_id), false);
assert.equal(window.IRON_PIT_BROWSER_SAVES.legalAction(action, hero, 10, "other-dragon"), true);

({ dragon, hero } = setupPair());
window.__saveRoll = 1;
window.IRON_PIT_BROWSER_SAVES.resolveAction(1, 1, dragon, hero, action, 10);
window.__saveRoll = 20;
const lifecycle = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(
  2, 1, hero, "target_turn_end",
);
assert.equal(lifecycle.events[0].save_succeeded, true);
assert.ok(!hero.state.active_effect_ids.includes("frightened"));
assert.equal(
  window.IRON_PIT_BROWSER_FAILED_SAVE_TIMED_EFFECTS.isImmune(hero, action, dragon.combatant_id),
  true,
);
console.log("Frightful Presence failed-save Frightened, success immunity, and printed name stay universal.");
