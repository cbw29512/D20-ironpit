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
window.IRON_PIT_BROWSER_MODIFIERS = {};
load("browser-terminal-effects.js");
load("browser-timed-conditions.js");
load("browser-failed-save-timed-effects.js");
load("browser-condition-lifecycle.js");

function member(id, side) {
  return {
    combatant_id: id,
    side,
    state: {
      template: { name: id, ruleset: "2014", condition_immunities: [] },
      current_hp: 10,
      is_alive: true,
      is_dead: false,
      is_unconscious: false,
      is_stable: false,
      active_effect_ids: [],
      timed_effects: [],
      active_modifiers: [],
      concentration: null,
      replacement_form: null,
    },
  };
}

const actor = member("Gorgon", "monsters");
const action = {
  id: "petrifying-breath",
  name: "Petrifying Breath",
  magicalEffect: false,
};
const rider = {
  effectId: "restrained",
  repeatSaveAbility: "constitution",
  repeatSaveDc: 13,
  repeatSaveTiming: "target_turn_end",
  repeatSaveFailureConditionId: "petrified",
};

function applyInitial(target) {
  const applied = window.IRON_PIT_BROWSER_FAILED_SAVE_TIMED_EFFECTS.apply(
    actor, target, action, rider, 1,
  );
  assert.equal(applied, "restrained");
  assert.ok(target.state.active_effect_ids.includes("restrained"));
  const effect = target.state.timed_effects.find(
    (item) => item.effect_id === "restrained",
  );
  assert.ok(effect);
  assert.equal(effect.repeat_save_ability, "constitution");
  assert.equal(effect.repeat_save_dc, 13);
  assert.equal(effect.repeat_save_timing, "target_turn_end");
  assert.equal(effect.repeat_save_failure_condition_id, "petrified");
}

{
  const target = member("Successful Target", "heroes");
  applyInitial(target);
  window.IRON_PIT_BROWSER_SAVES = {
    resolveSavingThrow: () => ({
      roll: { selected_roll: 20, total: 20, rolls: [20] },
      succeeded: true,
    }),
  };
  const result = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(
    1, 1, target, "target_turn_end",
  );
  assert.equal(result.events[0].save_succeeded, true);
  assert.equal(target.state.active_effect_ids.includes("restrained"), false);
  assert.equal(target.state.active_effect_ids.includes("petrified"), false);
  assert.equal(target.state.is_dead, false);
}

{
  const target = member("Failed Target", "heroes");
  applyInitial(target);
  window.IRON_PIT_BROWSER_SAVES = {
    resolveSavingThrow: () => ({
      roll: { selected_roll: 1, total: 1, rolls: [1] },
      succeeded: false,
    }),
  };
  const result = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(
    1, 1, target, "target_turn_end",
  );
  assert.equal(result.events[0].save_succeeded, false);
  assert.equal(target.state.active_effect_ids.includes("restrained"), false);
  assert.ok(target.state.active_effect_ids.includes("petrified"));
  assert.equal(target.state.is_dead, true);
  assert.equal(target.state.is_alive, false);
  assert.equal(target.state.current_hp, 0);
}

console.log("Browser failed-save timed effects reuse staged condition escalation.");
