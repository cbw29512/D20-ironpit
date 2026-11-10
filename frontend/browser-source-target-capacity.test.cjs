"use strict";

// Real browser timed-effect lifecycle and generic control capacity, no monster IDs.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = {
  immune: (state, id, _template, opts = {}) =>
    Boolean(state.counterMagical && id === "charmed" && opts.sourceIsMagical),
};
load("browser-timed-conditions.js");
load("browser-source-target-capacity.js");
load("browser-failed-save-timed-effects.js");

function member(id) {
  return {
    combatant_id: id,
    state: {
      template: { id, name: id, condition_immunities: [] },
      current_round: 1, turns_started: 0, active_effect_ids: [],
      timed_effects: [], active_curses: [], active_modifiers: [],
    },
  };
}
const actor = member("owner");
const targets = [member("a"), member("b"), member("c")];
const setup = { monsters: [actor], heroes: targets };
const action = { id: "renamed-control", name: "Unrelated Control", magicalEffect: true };
const rider = {
  effectId: "charmed", durationRounds: 14400, expiryTiming: "target_turn_end",
  sourceTargetLimit: 1, sourceEffectImmunityOnEnd: true,
};
const apply = (victim, config = rider) =>
  window.IRON_PIT_BROWSER_FAILED_SAVE_TIMED_EFFECTS.apply(
    actor, victim, action, config, 1, setup,
  );
const owned = (victim) => victim.state.timed_effects.filter((effect) =>
  effect.effect_id === "charmed" && effect.source_id === actor.combatant_id
    && effect.source_effect_id === action.id,
);
const immune = (victim) =>
  window.IRON_PIT_BROWSER_FAILED_SAVE_TIMED_EFFECTS.isImmune(
    victim, action, actor.combatant_id,
  );

try {
  assert.equal(apply(targets[0]), "charmed");
  assert.equal(owned(targets[0]).length, 1);
  assert.equal(apply(targets[1]), "charmed");
  assert.equal(owned(targets[0]).length, 0);
  assert.equal(owned(targets[1]).length, 1);
  assert.equal(immune(targets[0]), true);

  // An overlapping condition from a different actor remains, but the owner
  // whose control was displaced still becomes immune to that owner's effect.
  const overlapped = member("overlap");
  setup.heroes.push(overlapped);
  apply(overlapped);
  window.IRON_PIT_BROWSER_TIMED.apply(overlapped.state, "charmed", "other-owner", {
    sourceEffectId: "other-effect", sourceIsMagical: false,
    useDefaultPoisonRecovery: false,
  });
  apply(targets[2]);
  assert.equal(owned(overlapped).length, 0);
  assert.equal(overlapped.state.timed_effects.some((effect) =>
    effect.effect_id === "charmed" && effect.source_id === "other-owner"), true);
  assert.equal(immune(overlapped), true);

  // A freshly rejected control must not remove the old active control.
  targets[0].state.counterMagical = true;
  assert.equal(apply(targets[0]), null);
  assert.equal(owned(targets[2]).length, 1);

  // A two-target cap retains two newest conditions, not the oldest.
  const two = { ...rider, sourceTargetLimit: 2 };
  const fresh = [member("t1"), member("t2"), member("t3")];
  setup.heroes.push(...fresh);
  apply(fresh[0], two);
  apply(fresh[1], two);
  apply(fresh[2], two);
  assert.equal(owned(fresh[0]).length, 0);
  assert.equal(owned(fresh[1]).length, 1);
  assert.equal(owned(fresh[2]).length, 1);

  // Invalid capacity fails closed; no silent unbounded control.
  assert.throws(() =>
    window.IRON_PIT_BROWSER_SOURCE_TARGET_CAPACITY.enforce(
      actor, fresh[2], action.id, "charmed", 0, setup,
    ), /capacity/);
} catch (error) {
  console.error("Browser source-target capacity regression failed.", error);
  throw error;
}
console.log("Browser source-target capacity regressions passed.");
