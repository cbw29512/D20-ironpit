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
window.__saveRoll = 1;
window.IRON_PIT_BROWSER_SAVING_THROWS = {
  resolveSavingThrow: (_state, _ability, dc) => ({
    roll: { rolls: [window.__saveRoll], total: window.__saveRoll },
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
for (const file of [
  "browser-save-immunity.js", "browser-save-action-support.js", "browser-save-action-attempt.js",
  "browser-save-damage.js", "browser-save-damage-legacy.js", "browser-save-damage-apply.js",
  "browser-save-action-effects.js", "browser-save-event.js", "browser-saves.js",
  "browser-condition-lifecycle.js",
]) load(file);

function combatant(id, side) {
  return {
    combatant_id: id, side,
    state: {
      template: { name: id, creature_type: "humanoid" }, current_hp: 20,
      temporary_hp: 0, is_alive: true, is_dead: false, is_stable: false,
      death_save_successes: 0, death_save_failures: 0, active_effect_ids: [],
      timed_effects: [], active_modifiers: [], action_available: true,
      current_round: 1, resources: { "blindness-deafness": 1 },
    },
  };
}

const source = combatant("deep-gnome", "monsters");
const target = combatant("target", "heroes");
const action = {
  id: "blindness-deafness", name: "Blindness/Deafness", actionCost: "action",
  level: 2, range: 30, requiresTargetSight: true, saveAbility: "constitution", dc: 11,
  concentration: false,
  failedSaveTimedEffect: {
    effectId: "blinded", durationRounds: 10, expiryTiming: "target_turn_end",
    repeatSaveAbility: "constitution", repeatSaveDc: 11,
    repeatSaveTiming: "target_turn_end",
  },
};
const immutableAction = JSON.stringify(action);
let event = window.IRON_PIT_BROWSER_SAVES.resolveAction(1, 1, source, target, action, 5);
assert.equal(event.save_succeeded, false);
assert.deepEqual(event.applied_condition_ids, ["blinded"]);
const effect = target.state.timed_effects.find((item) => item.effect_id === "blinded");
assert.equal(effect.repeat_save_ability, "constitution");
assert.equal(effect.repeat_save_dc, 11);
assert.equal(effect.repeat_save_timing, "target_turn_end");
assert.equal(source.state.action_available, false);
assert.equal(source.state.concentration, undefined);

window.__saveRoll = 20;
event = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(
  2, 1, target, "target_turn_end", { monsters: [source], heroes: [target] },
).events[0];
assert.equal(event.save_succeeded, true);
assert.ok(!target.state.active_effect_ids.includes("blinded"));
assert.equal(JSON.stringify(action), immutableAction);
assert.equal(combatant("next-fight", "monsters").state.resources["blindness-deafness"], 1);

console.log("2014 innate Blindness failed-save, repeat-save, immutable action, and reset parity passed.");
