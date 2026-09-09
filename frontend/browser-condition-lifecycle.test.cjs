"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-grapple.js", "browser-state.js", "browser-rage.js", "browser-rolls.js",
  "browser-timed-conditions.js", "browser-zero-hp.js", "browser-forced-movement.js", "browser-control.js",
  "browser-attack-helpers.js", "browser-attack.js", "browser-resources.js", "browser-save-helpers.js",
  "browser-saves.js", "browser-condition-lifecycle.js",
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
  const target = member("repeat-save-target");
  T.apply(target.state, "frightened", "fear-source", {
    sourceEffectId: "fear-rider",
    appliedRound: 2,
    repeatSaveAbility: "wisdom",
    repeatSaveDc: 15,
    repeatSaveTiming: "target_turn_end",
  });

  const wrongTiming = L.resolveTargetTiming(1, 2, target, "target_turn_start");
  assert.equal(wrongTiming.events.length, 0, "A target-turn-end save must not fire at target-turn-start");
  assert.equal(target.state.active_effect_ids.includes("frightened"), true);

  d20 = 1;
  const failed = L.resolveTargetTiming(wrongTiming.sequence, 2, target, "target_turn_end");
  assert.equal(failed.events.length, 1);
  assert.equal(failed.events[0].save_succeeded, false);
  assert.equal(target.state.active_effect_ids.includes("frightened"), true);

  d20 = 20;
  const passed = L.resolveTargetTiming(failed.sequence, 3, target, "target_turn_end");
  assert.equal(passed.events.length, 1);
  assert.equal(passed.events[0].save_succeeded, true);
  assert.deepEqual(passed.events[0].removed_condition_ids, ["frightened"]);
  assert.equal(target.state.active_effect_ids.includes("frightened"), false);
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
  const source = member("fixed-duration-source");
  const target = member("fixed-duration-target");
  T.apply(target.state, "frightened", source.combatant_id, {
    sourceEffectId: "one-minute-fear",
    expiryTiming: "source_turn_start",
    expiresRound: 11,
  });
  const setup = { heroes: [source, target], monsters: [] };
  const early = L.resolveSourceTiming(1, 10, source, setup, "source_turn_start");
  assert.equal(early.events.length, 0, "Explicit source-relative durations must not expire early");
  assert.equal(target.state.active_effect_ids.includes("frightened"), true);
  const due = L.resolveSourceTiming(early.sequence, 11, source, setup, "source_turn_start");
  assert.equal(due.events.length, 1);
  assert.deepEqual(due.events[0].removed_condition_ids, ["frightened"]);
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

console.log("Browser condition lifecycle exact-timing regressions passed.");
