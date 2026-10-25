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
  resolveSavingThrow: (_state, _ability, dc) => ({
    roll: { total: window.__saveTotal },
    succeeded: window.__saveTotal >= dc,
  }),
  saveMode: () => "normal",
};
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state) => state.action_available,
  spend: (state) => { state.action_available = false; },
};
window.IRON_PIT_BROWSER_STATE = { sizeAtMost: () => true, distance: () => 10 };
window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS = { saveAdvantageSourceNames: () => [] };
window.IRON_PIT_BROWSER_CONDITION_RULES = { canSee: () => true };
window.IRON_PIT_BROWSER_ATTACK = { applyDamage: () => null };
window.IRON_PIT_BROWSER_GRAPPLE = { apply: () => [] };
window.IRON_PIT_DICE = { rollMany: () => [] };
load("browser-saves.js");

function member(id, name) {
  return {
    combatant_id: id, side: id.startsWith("hero") ? "heroes" : "monsters",
    state: {
      template: { name, creature_type: "undead" },
      current_hp: 30, temporary_hp: 0, is_alive: true, is_dead: false,
      is_stable: false, death_save_successes: 0, death_save_failures: 0,
      active_effect_ids: [], timed_effects: [], active_modifiers: [],
      action_available: true, current_round: 1, resources: {},
    },
  };
}

const normalKey = "2014-dreadful-glare-mummy";
const lordKey = "2014-dreadful-glare-mummy-lord";
const base = {
  id: "dreadful-glare", name: "Dreadful Glare", actionCost: "action",
  saveAbility: "wisdom", range: 60, requiresTargetSight: true,
  requiresTargetToSeeSource: true, magicalEffect: true,
  failedSaveTimedEffect: {
    effectId: "frightened", durationRounds: 1, expiryTiming: "source_turn_end",
    failureMarginEscalation: { margin: 5, additionalConditionIds: ["paralyzed"] },
  },
};
const mummyAction = {
  ...base, dc: 11,
  sourceEffectImmunityKeysOnSuccess: [normalKey],
  sourceEffectImmunityKeysBlocking: [normalKey],
};
const lordAction = {
  ...base, dc: 16,
  sourceEffectImmunityKeysOnSuccess: [normalKey, lordKey],
  sourceEffectImmunityKeysBlocking: [lordKey],
};

let mummy = member("mummy-a", "Mummy"), hero = member("hero-a", "Hero");
window.__saveTotal = 8;
let event = window.IRON_PIT_BROWSER_SAVES.resolveAction(1, 1, mummy, hero, mummyAction, 10);
assert.deepEqual(event.applied_condition_ids, ["frightened"]);

mummy = member("mummy-a", "Mummy"); hero = member("hero-a", "Hero");
window.__saveTotal = 6;
event = window.IRON_PIT_BROWSER_SAVES.resolveAction(1, 1, mummy, hero, mummyAction, 10);
assert.deepEqual(event.applied_condition_ids, ["frightened", "paralyzed"]);

mummy = member("mummy-a", "Mummy"); hero = member("hero-a", "Hero");
window.__saveTotal = 20;
window.IRON_PIT_BROWSER_SAVES.resolveAction(1, 1, mummy, hero, mummyAction, 10);
assert.equal(window.IRON_PIT_BROWSER_SAVES.legalAction(
  mummyAction, hero, 10, "mummy-b", member("mummy-b", "Mummy"),
), false);
assert.equal(window.IRON_PIT_BROWSER_SAVES.legalAction(
  lordAction, hero, 10, "lord-a", member("lord-a", "Mummy Lord"),
), true);

const lord = member("lord-a", "Mummy Lord"); hero = member("hero-b", "Hero");
window.__saveTotal = 20;
window.IRON_PIT_BROWSER_SAVES.resolveAction(2, 1, lord, hero, lordAction, 10);
assert.equal(window.IRON_PIT_BROWSER_SAVES.legalAction(
  mummyAction, hero, 10, "mummy-b", member("mummy-b", "Mummy"),
), false);
assert.equal(window.IRON_PIT_BROWSER_SAVES.legalAction(
  lordAction, hero, 10, "lord-b", member("lord-b", "Mummy Lord"),
), false);

console.log("2014 Dreadful Glare fail-by-5 and shared success immunity parity passed.");
