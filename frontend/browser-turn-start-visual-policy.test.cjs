"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-staged-save-debuff.js"), "utf8"));
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-turn-start-visual-policy.js"), "utf8"));
const P = window.IRON_PIT_BROWSER_TURN_START_VISUAL_POLICY;
const basilisk = { sourceId: "source-1", sourceName: "Petrifying Gaze", rangeFt: 30, saveDc: 12 };
const medusa = { sourceId: "source-2", sourceName: "Petrifying Gaze", rangeFt: 30, saveDc: 14, immediatePetrificationMargin: 5 };
const facts = { distanceFt: 15, sourceActive: true, targetActive: true, sourceSeesTarget: true,
  targetSeesSource: true, targetImmune: false, sourcePrecedesTarget: false };
for (const rule of [basilisk, medusa]) {
  assert.equal(P.decide(rule, facts), "averted");
  assert.equal(P.decide(rule, { ...facts, sourcePrecedesTarget: true }), "save_required");
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
    "targetSeesSource", "targetImmune", "sourcePrecedesTarget"]) {
    assert.throws(() => P.decide(basilisk, { ...facts, [flag]: 1 }));
  }
  for (const value of [true, false, 9.5, "9"]) {
    assert.throws(() => P.resolveStage(medusa, value));
  }
} finally {
  console.error = priorError;
}

const generic = { ...basilisk, sourceName: "Other Trigger", initialDebuff: "slowed", terminalDebuff: "stunned" };
assert.equal(P.resolveStage(generic, 3), "slowed");
assert.equal(P.resolveStage(generic, 3, "slowed"), "stunned");
assert.equal(P.resolveStage(generic, 12, "slowed"), "clear");

// No explicit choice flag is needed for the approved automatic tactical policy.
assert.equal(P.decide(basilisk, { ...facts }), "averted");

const invalidRuleValues = ["", " ", null, 42, true];
const originalError = console.error;
console.error = () => {};
try {
  for (const value of invalidRuleValues) {
    assert.throws(() => P.validate({ ...basilisk, saveAbility: value }));
    assert.throws(() => P.validate({ ...basilisk, initialDebuff: value }));
    assert.throws(() => P.validate({ ...basilisk, terminalDebuff: value }));
  }
  assert.throws(() => P.validate({ ...basilisk, initialDebuff: "petrified" }));
} finally {
  console.error = originalError;
}
assert.equal(P.resolveStage({ ...basilisk, saveAbility: "constitution" }, 1), "restrained");

const earlier = P.initiativePrecedes(["gaze", "hero"], "gaze", "hero");
const later = P.initiativePrecedes(["hero", "gaze"], "gaze", "hero");
assert.equal(earlier, true, "Gaze first: victim must save");
assert.equal(later, false, "Target first: automatically averts");
assert.equal(P.decide({ ...basilisk, sourceName: "Pregen", saveDc: 11 }, { ...facts, sourcePrecedesTarget: earlier }), "save_required");
assert.equal(P.decide({ ...basilisk, sourceName: "Homebrew" }, { ...facts, sourcePrecedesTarget: later }), "averted");
assert.throws(() => P.initiativePrecedes(["hero", "hero", "gaze"], "gaze", "hero"));
assert.throws(() => P.initiativePrecedes(["hero", "gaze"], "gaze", "unknown"));
assert.throws(() => P.initiativePrecedes([], "gaze", "hero"));
