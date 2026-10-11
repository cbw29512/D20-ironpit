"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
let saveSuccess = false;
const save = () => ({
  roll: { selected_roll: saveSuccess ? 20 : 1, total: saveSuccess ? 20 : 1 },
  succeeded: saveSuccess,
});
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = {
  immune: (state, id) => (state.template.condition_immunities || []).includes(id),
};
window.IRON_PIT_BROWSER_SAVING_THROWS = { resolveSavingThrow: save };
window.IRON_PIT_BROWSER_SAVES = { resolveSavingThrow: save };
window.IRON_PIT_BROWSER_HEALING_POLICY = { swarm: () => false };
window.IRON_PIT_BROWSER_STATE = {
  effectiveMaxHp: (state) => state.template.max_hp,
  sizeAtMost: () => true,
};
for (const f of [
  "browser-timed-conditions.js", "browser-healing.js",
  "browser-on-hit-condition-save.js", "browser-condition-lifecycle.js",
]) load(f);
const onHit = window.IRON_PIT_BROWSER_ON_HIT_CONDITION_SAVE;
const timed = window.IRON_PIT_BROWSER_TIMED;
const heal = window.IRON_PIT_BROWSER_HEALING;
const lifecycle = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE;
const attack = {
  name: "Beard", onHitConditionSave: {
    saveAbility: "constitution", dc: 12, conditionId: "poisoned",
    durationRounds: 10, repeatSaveTiming: "target_turn_end",
    cannotRegainHitPoints: true,
  },
};
const member = (immune = false) => ({
  combatant_id: "target", side: "heroes",
  state: {
    template: { name: "Target", max_hp: 40,
      condition_immunities: immune ? ["poisoned"] : [] },
    current_hp: 12, timed_effects: [], active_effect_ids: [], active_modifiers: [],
    is_dead: false, is_alive: true, is_unconscious: false,
    death_save_successes: 0, death_save_failures: 0,
  },
});
{
  const target = member();
  saveSuccess = false;
  const outcome = onHit.resolve(target, attack, {}, 1, null,
    { combatant_id: "devil-one" });
  assert.equal(outcome.saveSucceeded, false);
  assert.equal(outcome.appliedCondition, "poisoned");
  assert.equal(target.state.timed_effects[0].cannot_regain_hit_points, true);
  assert.equal(target.state.timed_effects[0].expires_round, 11);
  assert.equal(heal.restore(target.state, 9), 0);
  saveSuccess = true;
  const turnEnd = lifecycle.resolveTargetTiming(2, 2, target, "target_turn_end");
  assert.equal(turnEnd.events[0].save_succeeded, true);
  assert.equal(target.state.timed_effects.length, 0);
  assert.equal(heal.restore(target.state, 9), 9);
}
{
  const target = member(true);
  saveSuccess = false;
  assert.equal(onHit.resolve(target, attack, {}, 1), null);
  assert.equal(target.state.timed_effects.length, 0);
  assert.equal(heal.restore(target.state, 5), 5);
}
console.log("2014 Beard generic on-hit Poisoned plus source-linked no-healing passed.");
