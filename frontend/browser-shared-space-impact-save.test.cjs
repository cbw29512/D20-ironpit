"use strict";

// The blocked 2014 card compiles this exact generic save shape. Prove browser
// save/typed damage/Prone semantics without adding a creature-name resolver.
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

try {
  const state = window.IRON_PIT_BROWSER_STATE;
  const fighter = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-2014-l5"];
  assert.ok(fighter, "A certified target is required");
  const member = (id, side) => ({
    combatant_id: id, side, position_ft: 0,
    state: state.buildState(structuredClone(fighter)),
  });
  const action = {
    id: "synthetic-squall", name: "Squall",
    actionCost: "action", saveAbility: "strength", dc: 13,
    range: 0, maxTargets: 20, targetScope: "all-other-creatures",
    area: {shape: "shared-space", origin: "self"},
    damageDiceCount: 3, damageDiceSize: 8, damageBonus: 2,
    damageType: "bludgeoning", successDamage: "half",
    failedSaveTimedEffect: {effectId: "prone", expiryTiming: null},
  };
  const dice = window.IRON_PIT_DICE;
  const originalRoll = dice.roll, originalMany = dice.rollMany;
  let saveRoll = 1;
  dice.roll = (sides) => sides === 20 ? saveRoll : 2;
  dice.rollMany = (count, sides) => Array.from(
    {length: count}, () => dice.roll(sides),
  );
  try {
    const source = member("source", "monsters");
    const failed = member("failed", "heroes");
    const passed = member("passed", "heroes");
    const setup = {monsters: [source], heroes: [failed, passed]};
    const priorPositions = [source.position_ft, failed.position_ft, passed.position_ft];
    const options = {spendAction: false, checkResource: false, spendResource: false, setup};
    const failedBefore = failed.state.current_hp;
    const failure = window.IRON_PIT_BROWSER_SAVES.resolveAction(
      1, 1, source, failed, action, 0, options,
    );
    assert.equal(failure.save_succeeded, false);
    assert.equal(failedBefore - failed.state.current_hp, 8);
    assert.ok(failed.state.active_effect_ids.includes("prone"));
    assert.ok(failure.applied_condition_ids.includes("prone"));
    assert.match(failure.description, /Squall/);
    saveRoll = 20;
    const passedBefore = passed.state.current_hp;
    const success = window.IRON_PIT_BROWSER_SAVES.resolveAction(
      2, 1, source, passed, action, 0, options,
    );
    assert.equal(success.save_succeeded, true);
    assert.equal(passedBefore - passed.state.current_hp, 4);
    assert.ok(!passed.state.active_effect_ids.includes("prone"));
    assert.ok(!success.applied_condition_ids.includes("prone"));
    assert.deepEqual(
      [source.position_ft, failed.position_ft, passed.position_ft],
      priorPositions, "Pit-forbidden fling never relocates combatants",
    );
  } finally {
    dice.roll = originalRoll;
    dice.rollMany = originalMany;
  }
  console.log("Shared-space impact save damage and Prone parity passed");
} catch (error) {
  console.error("Shared-space impact save browser regression failed", error);
  process.exitCode = 1;
}
