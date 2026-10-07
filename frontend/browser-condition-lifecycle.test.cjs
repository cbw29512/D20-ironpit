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
  "browser-rolls.js", "browser-terminal-effects.js", "browser-timed-conditions.js", "browser-failed-save-timed-effects.js", "browser-zero-hp.js", "browser-ability-hooks.js", "browser-attack-outcome.js", "browser-attack.js", "browser-saving-throws.js", "browser-saves.js",
  "browser-condition-lifecycle.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const T = window.IRON_PIT_BROWSER_TIMED;
const L = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE;
const template = () => structuredClone(window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"]);
const member = (id, side = "heroes") => ({ combatant_id: id, side, position_ft: 0, state: S.buildState(template()) });
let d20 = 1;
window.IRON_PIT_DICE = {
  roll: (sides) => sides === 20 ? d20 : 1,
  rollMany: (count, sides) => Array.from({ length: count }, () => sides === 20 ? d20 : 1),
};

{
  const target = member("poison-recovery-target");
  T.apply(target.state, "poisoned", "venom-source", {
    sourceEffectId: "venom-rider",
    appliedRound: 2,
    repeatSaveAbility: "constitution",
    repeatSaveDc: 15,
    repeatSaveTiming: "target_turn_end",
  });

  const sameRound = L.resolveTargetTiming(1, 2, target, "target_turn_start");
  assert.equal(sameRound.events.length, 0, "Poisoned must last through the round in which it is applied");
  assert.equal(target.state.active_effect_ids.includes("poisoned"), true);

  d20 = 1;
  const failed = L.resolveTargetTiming(sameRound.sequence, 3, target, "target_turn_start");
  assert.equal(failed.events.length, 1);
  assert.equal(failed.events[0].save_succeeded, false);
  assert.equal(target.state.active_effect_ids.includes("poisoned"), true);

  d20 = 20;
  const passed = L.resolveTargetTiming(failed.sequence, 4, target, "target_turn_start");
  assert.equal(passed.events.length, 1);
  assert.equal(passed.events[0].save_succeeded, true);
  assert.deepEqual(passed.events[0].removed_condition_ids, ["poisoned"]);
  assert.equal(target.state.active_effect_ids.includes("poisoned"), false);
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
  const target = member("end-turn-removal-target");
  target.state.template.end_turn_condition_removal = {
    source_id: "test-restoration",
    source_name: "Test Restoration",
    condition_ids: ["charmed", "frightened", "poisoned"],
    max_conditions: 1,
  };
  T.apply(target.state, "poisoned", "poison-source", {
    sourceEffectId: "poison-test",
    useDefaultPoisonRecovery: false,
  });
  T.apply(target.state, "charmed", "charm-source", {
    sourceEffectId: "charm-test",
    useDefaultPoisonRecovery: false,
  });
  const result = L.resolveTargetTiming(1, 6, target, "target_turn_end");
  assert.equal(result.events.length, 1);
  assert.equal(result.events[0].feature_id, "test-restoration");
  assert.deepEqual(result.events[0].removed_condition_ids, ["charmed"]);
  assert.equal(target.state.active_effect_ids.includes("charmed"), false);
  assert.equal(target.state.active_effect_ids.includes("poisoned"), true);
}

{
  const source = member("gorgon", "monsters");
  const target = member("gorgon-target");
  const action = { id: "petrifying-breath", name: "Petrifying Breath", magicalEffect: false };
  const rider = {
    effectId: "restrained",
    repeatSaveAbility: "constitution",
    repeatSaveDc: 13,
    repeatSaveTiming: "target_turn_end",
    repeatSaveFailureConditionId: "petrified",
  };
  const applied = window.IRON_PIT_BROWSER_FAILED_SAVE_TIMED_EFFECTS.apply(
    source, target, action, rider, 1,
  );
  assert.equal(applied, "restrained");
  assert.equal(target.state.active_effect_ids.includes("restrained"), true);
  assert.equal(target.state.is_dead, false);

  d20 = 1;
  const result = L.resolveTargetTiming(
    1, 1, target, "target_turn_end", { heroes: [target], monsters: [source] },
  );
  assert.equal(result.events.length, 1);
  assert.equal(result.events[0].save_succeeded, false);
  assert.deepEqual(result.events[0].applied_condition_ids, ["petrified"]);
  assert.equal(target.state.active_effect_ids.includes("restrained"), false);
  assert.equal(target.state.active_effect_ids.includes("petrified"), true);
  assert.equal(target.state.is_dead, true);
  assert.equal(target.state.current_hp, 0);
}

console.log("Browser condition lifecycle regressions passed.");
