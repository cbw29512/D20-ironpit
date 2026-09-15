"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-condition-immunity.js", "browser-condition-rules.js",
  "browser-action-economy.js", "browser-grapple.js", "browser-state.js", "browser-rage.js",
  "browser-rolls.js", "browser-timed-conditions.js", "browser-zero-hp.js", "browser-attack.js", "browser-saves.js",
  "browser-condition-lifecycle.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const T = window.IRON_PIT_BROWSER_TIMED;
const L = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE;
const template = () => structuredClone(window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"]);
const member = (id, side = "heroes") => ({ combatant_id: id, side, position_ft: 0, state: S.buildState(template()) });
let d20 = 1, damageDie = 1;
window.IRON_PIT_DICE = {
  roll: (sides) => sides === 20 ? d20 : damageDie,
  rollMany: (count, sides) => Array.from({ length: count }, () => sides === 20 ? d20 : damageDie),
};

{
  const target = member("repeat-save-target");
  T.apply(target.state, "frightened", "fear-source", {
    sourceEffectId: "fear-rider",
    appliedRound: 2,
    expiresAtStartOfSourceTurn: false,
    repeatSaveAbility: "constitution",
    repeatSaveDc: 15,
    repeatSaveTiming: "target_turn_start",
    repeatSaveDelayRounds: 1,
  });

  const sameRound = L.resolveTargetTiming(1, 2, target, "target_turn_start");
  assert.equal(sameRound.events.length, 0, "explicit repeat-save delay must suppress same-round recovery");
  assert.equal(target.state.active_effect_ids.includes("frightened"), true);

  d20 = 1;
  const failed = L.resolveTargetTiming(sameRound.sequence, 3, target, "target_turn_start");
  assert.equal(failed.events.length, 1);
  assert.equal(failed.events[0].save_succeeded, false);
  assert.equal(target.state.active_effect_ids.includes("frightened"), true);

  d20 = 20;
  const passed = L.resolveTargetTiming(failed.sequence, 4, target, "target_turn_start");
  assert.equal(passed.events.length, 1);
  assert.equal(passed.events[0].save_succeeded, true);
  assert.deepEqual(passed.events[0].removed_condition_ids, ["frightened"]);
  assert.equal(target.state.active_effect_ids.includes("frightened"), false);
}

{
  const target = member("staged-repeat-save-target");
  T.apply(target.state, "incapacitated", "silver-dragon", {
    sourceEffectId: "paralyzing-breath", appliedRound: 3,
    repeatSaveAbility: "constitution", repeatSaveDc: 13, repeatSaveTiming: "target_turn_end",
    repeatSaveFailureCondition: "paralyzed", automaticSuccessAfterRounds: 10,
  });
  d20 = 1;
  const escalated = L.resolveTargetTiming(1, 4, target, "target_turn_end");
  assert.deepEqual(escalated.events[0].removed_condition_ids, ["incapacitated"]);
  assert.deepEqual(escalated.events[0].applied_condition_ids, ["paralyzed"]);
  const effect = target.state.timed_effects.find((item) => item.effect_id === "paralyzed");
  assert.ok(effect);
  assert.equal(effect.repeat_save_ability, "constitution");
  assert.equal(effect.repeat_save_dc, 13);
  assert.equal(effect.repeat_save_timing, "target_turn_end");
  assert.equal(effect.repeat_save_failure_condition, null);
  assert.equal(effect.automatic_success_round, 13);
  d20 = 20;
  const recovered = L.resolveTargetTiming(escalated.sequence, 5, target, "target_turn_end");
  assert.equal(recovered.events[0].save_succeeded, true);
  assert.deepEqual(recovered.events[0].removed_condition_ids, ["paralyzed"]);
}

{
  const source = member("source");
  const target = member("expiry-target");
  T.apply(target.state, "frightened", source.combatant_id, {
    sourceEffectId: "fear-effect",
    expiryTiming: "source_turn_start",
  });
  const setup = { heroes: [source, target], monsters: [] };
  const result = L.resolveSourceTiming(1, 4, source, setup, "source_turn_start");
  assert.equal(result.events.length, 1);
  assert.deepEqual(result.events[0].removed_condition_ids, ["frightened"]);
  assert.equal(target.state.active_effect_ids.includes("frightened"), false);
}

{
  const sourceA = member("source-a"), sourceB = member("source-b"), target = member("multi-source-target");
  T.apply(target.state, "frightened", sourceA.combatant_id, { sourceEffectId: "fear-a", expiryTiming: "source_turn_start" });
  T.apply(target.state, "frightened", sourceB.combatant_id, { sourceEffectId: "fear-b", expiryTiming: "source_turn_start" });
  const setup = { heroes: [sourceA, sourceB, target], monsters: [] };
  const first = L.resolveSourceTiming(1, 5, sourceA, setup, "source_turn_start");
  assert.equal(first.events.length, 0, "One source ending must not clear a condition still supplied by another source");
  assert.equal(target.state.active_effect_ids.includes("frightened"), true);
  const second = L.resolveSourceTiming(first.sequence, 5, sourceB, setup, "source_turn_start");
  assert.equal(second.events.length, 1);
  assert.equal(target.state.active_effect_ids.includes("frightened"), false);
}

{
  const target = member("periodic-target");
  const hpBefore = target.state.current_hp;
  T.apply(target.state, "poisoned", "vrock-source", {
    sourceEffectId: "spores", appliedRound: 1,
    repeatSaveAbility: "constitution", repeatSaveDc: 14, repeatSaveTiming: "target_turn_end",
    periodicDamage: { timing: "target_turn_start", diceCount: 1, diceSize: 10, damageBonus: 0, damageType: "poison" },
  });
  damageDie = 9;
  const tick = L.resolveTargetTiming(1, 2, target, "target_turn_start");
  assert.equal(tick.events.length, 1);
  assert.equal(tick.events[0].damage_components[0].applied_total, 9);
  assert.equal(target.state.current_hp, hpBefore - 9);
  d20 = 20;
  const recovery = L.resolveTargetTiming(tick.sequence, 2, target, "target_turn_end");
  assert.equal(recovery.events[0].save_succeeded, true);
  assert.deepEqual(recovery.events[0].removed_condition_ids, ["poisoned"]);
}

console.log("Browser condition lifecycle regressions passed.");