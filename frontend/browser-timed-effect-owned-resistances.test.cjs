"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-timed-conditions.js"), "utf8"),
  { filename: "browser-timed-conditions.js" },
);

const timed = window.IRON_PIT_BROWSER_TIMED;
const state = { active_effect_ids: [], timed_effects: [] };

timed.apply(state, "empty-body", "monk", {
  sourceEffectId: "empty-body",
  appliedRound: 1,
  expiresRound: 11,
  expiryTiming: "source_turn_start",
  ownedDamageResistances: ["acid", "cold", "fire"],
});
timed.apply(state, "ward", "ally", {
  sourceEffectId: "ward",
  appliedRound: 1,
  expiresRound: 3,
  expiryTiming: "source_turn_start",
  ownedDamageResistances: ["fire"],
});

assert.equal(timed.ownsDamageResistance(state, "fire"), true);
assert.equal(timed.ownsDamageResistance(state, "force"), false);
assert.deepEqual(state.temporary_damage_resistances, undefined,
  "source-owned timed resistance must not mutate legacy pooled resistance state");

const ward = state.timed_effects.find((effect) => effect.source_effect_id === "ward");
assert.equal(timed.removeEffect(state, ward), true);
assert.equal(timed.ownsDamageResistance(state, "fire"), true,
  "removing one source must preserve overlapping resistance owned by another source");

const emptyBody = state.timed_effects.find((effect) => effect.source_effect_id === "empty-body");
assert.equal(timed.removeEffect(state, emptyBody), true);
assert.equal(timed.ownsDamageResistance(state, "fire"), false,
  "resistance ends when its final owning timed effect ends");

console.log("Browser timed-effect resistance ownership lifecycle is certified.");
