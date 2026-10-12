"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = (file) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, file), "utf8"), { filename: file },
);

window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
load("browser-effective-senses.js");
load("browser-condition-rules.js");
load("browser-state.js");
const E = window.IRON_PIT_BROWSER_EFFECTIVE_SENSES;
const C = window.IRON_PIT_BROWSER_CONDITION_RULES;
const S = window.IRON_PIT_BROWSER_STATE;
const source = {
  id: "source-bounded-blindsight", name: "Source-Bound Senses", kind: "monster",
  ruleset: "2014", max_hp: 20, speed_ft: 30, size: "medium", resources: {},
  blindsight_ft: 30, blindsight_deafened_ft: 10, truesight_ft: 0,
  blind_beyond_blindsight: true, blindsight_requires_smell_when_deafened: true,
};
const normal = { ...source, id: "control", blindsight_ft: 0, blindsight_deafened_ft: null,
  blind_beyond_blindsight: false, blindsight_requires_smell_when_deafened: false };
const observer = S.buildState(source);
const target = S.buildState(normal);
assert.equal(E.sourceSenseRangeFt(observer, "blindsight"), 30);
assert.equal(E.effectiveSenseRangeFt(observer, "blindsight"), 30);
assert.equal(C.canSee(observer, target, 30), true);
assert.equal(C.canSee(observer, target, 35), false, "blind beyond radius is not ordinary sight");
assert.equal(C.canSee(target, observer, 35), true, "normal sight stays intact");
observer.active_effect_ids.push("deafened");
assert.equal(E.effectiveSenseRangeFt(observer, "blindsight"), 10);
assert.equal(C.canSee(observer, target, 10), true);
assert.equal(C.canSee(observer, target, 15), false);
observer.suppressed_sense_ids.push("smell");
assert.equal(E.effectiveSenseRangeFt(observer, "blindsight"), 0);
assert.equal(C.canSee(observer, target, 5), false);
observer.active_effect_ids = [];
assert.equal(E.effectiveSenseRangeFt(observer, "blindsight"), 30, "smell alone does not end Blindsight");
observer.suppressed_sense_ids = [];
assert.equal(E.effectiveSenseRangeFt(observer, "blindsight"), 30);
const unseen = S.buildState({ ...normal, id: "hidden" });
unseen.active_effect_ids.push("invisible");
assert.equal(C.canSee(observer, unseen, 30), true);
assert.equal(C.canSee(observer, unseen, 35), false);
const newFight = S.buildState(source);
assert.deepEqual(newFight.suppressed_sense_ids, []);
assert.deepEqual(newFight.active_effect_ids, []);
assert.equal(C.canSee(newFight, target, 30), true);
assert.equal(C.canSee(S.buildState(normal), target, 35), true);
console.log("2014 source-bound bounded Blindsight browser semantics passed.");
