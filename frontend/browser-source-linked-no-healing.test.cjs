"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = {
  immune: (state, id) => (state.template.condition_immunities || []).includes(id),
};
window.IRON_PIT_BROWSER_HEALING_POLICY = { swarm: () => false };
window.IRON_PIT_BROWSER_STATE = { effectiveMaxHp: (state) => state.template.max_hp };
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
load("browser-timed-conditions.js");
load("browser-healing.js");
const timed = window.IRON_PIT_BROWSER_TIMED;
const heal = window.IRON_PIT_BROWSER_HEALING;
const state = () => ({
  template: { name: "Target", max_hp: 20 }, current_hp: 1,
  active_effect_ids: [], timed_effects: [], active_modifiers: [],
  is_dead: false, is_alive: true, is_unconscious: false, is_stable: false,
  death_save_successes: 0, death_save_failures: 0,
});
const beard = {
  sourceEffectId: "Beard", cannotRegainHitPoints: true,
  expiryTiming: "target_turn_end", expiresRound: 11, appliedRound: 1,
  repeatSaveAbility: "constitution", repeatSaveDc: 12,
  repeatSaveTiming: "target_turn_end", useDefaultPoisonRecovery: false,
};
{
  const target = state();
  assert.equal(timed.apply(target, "poisoned", "devil-one", beard), "poisoned");
  assert.equal(heal.restore(target, 8), 0);
  assert.equal(target.current_hp, 1);
  timed.removeEffect(target, target.timed_effects[0]);
  assert.equal(heal.restore(target, 8), 8);
  assert.equal(target.current_hp, 9);
}
{
  const target = state();
  timed.apply(target, "poisoned", "devil-one", beard);
  timed.apply(target, "poisoned", "devil-two", {
    sourceEffectId: "ordinary-poison", useDefaultPoisonRecovery: false,
  });
  assert.equal(heal.restore(target, 5), 0);
  timed.removeEffect(target, target.timed_effects.find((e) => e.source_id === "devil-one"));
  assert.ok(target.active_effect_ids.includes("poisoned"));
  assert.equal(heal.restore(target, 5), 5);
}
{
  const target = state();
  target.template.condition_immunities = ["poisoned"];
  assert.equal(timed.apply(target, "poisoned", "devil-one", beard), null);
  assert.equal(target.timed_effects.length, 0);
  assert.equal(heal.restore(target, 5), 5);
}
console.log("Source-scoped timed healing block regressions passed.");
