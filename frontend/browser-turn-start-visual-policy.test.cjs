"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-turn-start-visual-policy.js"), "utf8"));
const P = window.IRON_PIT_BROWSER_TURN_START_VISUAL_POLICY;
const basilisk = { sourceId: "source-1", sourceName: "Petrifying Gaze", rangeFt: 30, saveDc: 12 };
const medusa = { sourceId: "source-2", sourceName: "Petrifying Gaze", rangeFt: 30, saveDc: 14, immediatePetrificationMargin: 5 };
const facts = { distanceFt: 15, sourceActive: true, targetActive: true, sourceSeesTarget: true,
  targetSeesSource: true, targetImmune: false, targetSurprised: false, avertsEyes: true };
for (const rule of [basilisk, medusa]) {
  assert.equal(P.decide(rule, facts), "averted");
  assert.equal(P.decide(rule, { ...facts, avertsEyes: false }), "save_required");
  assert.equal(P.decide(rule, { ...facts, targetSurprised: true }), "save_required");
  for (const patch of [{ distanceFt: 31 }, { sourceActive: false }, { targetActive: false },
    { sourceSeesTarget: false }, { targetSeesSource: false }, { targetImmune: true }]) {
    assert.equal(P.decide(rule, { ...facts, ...patch }), "ineligible");
  }
}
assert.equal(P.resolveStage(basilisk, 1), "restrained");
assert.equal(P.resolveStage(basilisk, 12), "clear");
assert.equal(P.resolveStage(basilisk, 1, "restrained"), "petrified");
assert.equal(P.resolveStage(basilisk, 12, "restrained"), "clear");
assert.equal(P.resolveStage(medusa, 10), "restrained");
assert.equal(P.resolveStage(medusa, 9), "petrified");
assert.equal(P.resolveStage({ ...medusa, sourceName: "Unrelated Label" }, 9), "petrified");
assert.throws(() => P.resolveStage(medusa, 4, "unknown"), /Invalid visual stage/);
assert.throws(() => P.decide(medusa, { ...facts, distanceFt: -1 }), /Invalid visual distance/);
console.log("Visual policy browser regressions passed.");

const priorError = console.error;
console.error = () => {};
try {
  for (const value of [true, 30.5, "30"]) {
    assert.throws(() => P.validate({ ...basilisk, rangeFt: value }));
  }
  for (const value of [true, 12.5, "12"]) {
    assert.throws(() => P.validate({ ...basilisk, saveDc: value }));
  }
  for (const value of [true, 15.5, "15"]) {
    assert.throws(() => P.decide(basilisk, { ...facts, distanceFt: value }));
  }
  for (const flag of ["sourceActive", "targetActive", "sourceSeesTarget",
    "targetSeesSource", "targetImmune", "targetSurprised", "avertsEyes"]) {
    assert.throws(() => P.decide(basilisk, { ...facts, [flag]: 1 }));
  }
  for (const value of [true, false, 9.5, "9"]) {
    assert.throws(() => P.resolveStage(medusa, value));
  }
} finally {
  console.error = priorError;
}
