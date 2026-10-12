"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
load("browser-effective-senses.js");
load("browser-condition-rules.js");
load("browser-state.js");
load("browser-timed-conditions.js");
load("browser-condition-removal.js");

const C = window.IRON_PIT_BROWSER_CONDITION_RULES;
const S = window.IRON_PIT_BROWSER_STATE;
const T = window.IRON_PIT_BROWSER_TIMED;
const R = window.IRON_PIT_BROWSER_CONDITION_REMOVAL;
const template = {
  id: "innate-example", name: "Innate Invisible Source", kind: "monster",
  ruleset: "2014", max_hp: 50, speed_ft: 30, size: "medium",
  resources: {}, innate_condition_ids: ["invisible"],
};
const state = S.buildState(template);
const ordinary = S.buildState({ ...template, id: "observer", innate_condition_ids: [] });
const seer = S.buildState({ ...template, id: "seer", innate_condition_ids: [], truesight_ft: 30 });
assert.deepEqual(state.active_effect_ids, ["invisible"]);
assert.equal(C.has(state, "invisible"), true);
assert.equal(C.canSee(ordinary, state, 5), false);
assert.equal(C.canSee(seer, state, 5), true);
state.active_modifiers.push({ kind: "invisibility-benefits-suppressed" });
assert.equal(C.canSee(ordinary, state, 5), true);
state.active_modifiers.length = 0;

T.apply(state, "invisible", "temporary-spell", { sourceEffectId: "temporary-spell", appliedRound: 1 });
assert.equal(state.timed_effects.length, 1);
assert.deepEqual(T.removeGroup(state, state.timed_effects[0]), []);
assert.equal(state.timed_effects.length, 0);
assert.deepEqual(state.active_effect_ids, ["invisible"]);
assert.equal(C.has(state, "invisible"), true);

R.removeCondition({ combatant_id: "source", state }, "invisible");
assert.deepEqual(state.active_effect_ids, ["invisible"]);
assert.equal(C.canSee(ordinary, state, 5), false);
state.active_effect_ids = [];
assert.equal(C.has(state, "invisible"), true, "innate condition predicate must survive independent state cleanup");
const reset = S.buildState(template);
assert.deepEqual(reset.active_effect_ids, ["invisible"]);
assert.deepEqual(reset.timed_effects, []);
assert.deepEqual(S.buildState({ ...template, innate_condition_ids: [] }).active_effect_ids, []);

console.log("Universal innate conditions Python/browser semantics: browser parity passed.");
