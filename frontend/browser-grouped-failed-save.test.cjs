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
  resolveSavingThrow: () => ({ roll: 1, succeeded: false }),
  saveMode: () => "normal",
};
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "action" && state.action_available,
  spend: (state) => { state.action_available = false; },
};
window.IRON_PIT_BROWSER_STATE = { sizeAtMost: () => true };
window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS = { saveAdvantageSourceNames: () => [] };
window.IRON_PIT_BROWSER_CONDITION_RULES = { canSee: () => true };
window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage: (_state, amount) => amount,
  applyDamage: () => null,
};
window.IRON_PIT_BROWSER_GRAPPLE = { apply: () => [] };
window.IRON_PIT_DICE = { rollMany: () => [] };
load("browser-saves.js");

function combatant(id, side) {
  return {
    combatant_id: id,
    side,
    state: {
      template: { name: id, creature_type: "humanoid" },
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

const source = combatant("source", "monsters");
const target = combatant("target", "heroes");
const action = {
  id: "renamed-group-control",
  name: "Renamed Group Control",
  actionCost: "action",
  saveAbility: "wisdom",
  dc: 16,
  range: 30,
  failedSaveTimedEffect: {
    effectId: "charmed",
    additionalEffectIds: ["incapacitated"],
    repeatSaveAbility: "wisdom",
    repeatSaveDc: 16,
    repeatSaveTiming: "target_turn_end",
  },
};
const immutableCard = JSON.stringify(action);

const event = window.IRON_PIT_BROWSER_SAVES.resolveAction(
  1, 1, source, target, action, 5,
);

assert.deepEqual(event.applied_condition_ids, ["charmed", "incapacitated"]);
assert.deepEqual(target.state.active_effect_ids, ["charmed", "incapacitated"]);
const primary = target.state.timed_effects.find((item) => item.effect_id === "charmed");
const secondary = target.state.timed_effects.find(
  (item) => item.effect_id === "incapacitated",
);
assert.equal(primary.repeat_save_timing, "target_turn_end");
assert.equal(secondary.repeat_save_timing, null);
assert.equal(primary.source_effect_id, secondary.source_effect_id);
assert.deepEqual(
  window.IRON_PIT_BROWSER_TIMED.removeGroup(target.state, primary),
  ["charmed", "incapacitated"],
);
assert.deepEqual(target.state.active_effect_ids, []);
assert.equal(JSON.stringify(action), immutableCard);
console.log("Grouped failed-save conditions share one immutable-card lifecycle.");
