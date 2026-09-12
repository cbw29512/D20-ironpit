"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-condition-immunity.js", "browser-state.js", "browser-timed-conditions.js",
  "browser-modifiers.js", "browser-condition-lifecycle.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const T = window.IRON_PIT_BROWSER_TIMED;
const L = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE;
const state = S.buildState(structuredClone(window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"]));
const target = { combatant_id: "target", side: "heroes", position_ft: 0, state };

T.apply(state, "unconscious", "source", {
  sourceEffectId: "sleep-effect",
  appliedRound: 2,
  expiresRound: 12,
  expiryTiming: "target_turn_end",
});

const early = L.resolveTargetTiming(1, 3, target, "target_turn_end");
assert.equal(early.events.length, 0);
assert.equal(state.active_effect_ids.includes("unconscious"), true);

const due = L.resolveTargetTiming(early.sequence, 12, target, "target_turn_end");
assert.equal(due.events.length, 1);
assert.deepEqual(due.events[0].removed_condition_ids, ["unconscious"]);
assert.equal(state.active_effect_ids.includes("unconscious"), false);

console.log("Browser timed condition expiry-round regression passed.");
