"use strict";

const { assert, attack, dice, member } = require("./browser-on-hit-condition-test-support.cjs");

try {
  const fighter = member("petrifier", "heroes", {
    onHitConditionSave: {
      saveAbility: "constitution", dc: 12, conditionId: "petrified",
    },
  });
  const target = member("petrified-target", "monsters", { position: 5 });
  const event = attack(fighter, target, [15, 4, 4, 1]);
  assert.equal(event.save_succeeded, false);
  assert.ok(target.state.active_effect_ids.includes("petrified"));
  assert.equal(target.state.is_dead, true);
  assert.equal(target.state.is_alive, false);
  assert.equal(target.state.current_hp, 0);
} catch (error) {
  console.error("Immediate terminal on-hit condition regression failed", { error });
  throw error;
}

try {
  const fighter = member("staged-petrifier", "heroes", {
    onHitConditionSave: {
      saveAbility: "constitution", dc: 12, conditionId: "restrained",
      repeatSaveTiming: "target_turn_end",
      repeatSaveFailureConditionId: "petrified",
    },
  });
  const target = member("staged-target", "monsters", { position: 5 });
  const first = attack(fighter, target, [15, 4, 4, 1]);
  assert.equal(first.save_succeeded, false);
  assert.ok(target.state.active_effect_ids.includes("restrained"));
  assert.equal(target.state.is_dead, false);

  dice([1]);
  const lifecycle = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(
    2, 1, target, "target_turn_end",
  );
  assert.equal(lifecycle.events[0].save_succeeded, false);
  assert.ok(target.state.active_effect_ids.includes("petrified"));
  assert.equal(target.state.active_effect_ids.includes("restrained"), false);
  assert.equal(target.state.is_dead, true);
  assert.equal(target.state.current_hp, 0);
} catch (error) {
  console.error("Staged terminal on-hit condition regression failed", { error });
  throw error;
}

console.log("Browser terminal on-hit condition regressions passed.");
