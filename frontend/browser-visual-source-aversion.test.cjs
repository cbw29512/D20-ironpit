"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
for (const name of ["browser-visual-source-aversion.js", "browser-turn-start-visual-policy.js"]) {
  vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"));
}
const A = window.IRON_PIT_BROWSER_VISUAL_SOURCE_AVERSION;
const P = window.IRON_PIT_BROWSER_TURN_START_VISUAL_POLICY;
const first = A.record([], "observer", "source-a", 1);
assert.equal(A.active(first, "observer", "source-a", 1), true);
assert.equal(A.active(first, "observer", "source-b", 1), false);
assert.equal(A.active(first, "observer", "source-a", 2), false);
assert.equal(A.active([], "observer", "source-a", 1), false);
assert.deepEqual(A.perceive(first, "observer", "source-a", 1, true, true),
  { visualSight: false, canPerceive: true });
assert.deepEqual(A.perceive(first, "observer", "source-b", 1, true, false),
  { visualSight: true, canPerceive: true });
const second = A.record(first, "observer", "source-b", 1);
assert.equal(second.length, 2);
assert.equal(first.length, 1);
assert.equal(A.record(second, "observer", "source-a", 2).length, 1);
const rule = { sourceId: "source-trait", sourceName: "Printed Name", rangeFt: 30, saveDc: 12 };
const facts = { distanceFt: 15, sourceActive: true, targetActive: true,
  sourceSeesTarget: true, targetImmune: false, targetSurprised: false, avertsEyes: false };
assert.equal(P.decide(rule, { ...facts, targetSeesSource: false }), "ineligible");
assert.equal(P.decide(rule, { ...facts, targetSeesSource: true }), "save_required");
const oldError = console.error;
console.error = () => {};
try {
  assert.throws(() => A.record([], "", "source", 1));
  assert.throws(() => A.record([], "observer", "source", true));
  assert.throws(() => A.active([{ observerId: "observer", sourceId: "source",
    expiresOnObserverTurnStart: -1 }], "observer", "source", 1));
  assert.throws(() => A.perceive([{ observerId: "observer", sourceId: "source",
    expiresOnObserverTurnStart: -1 }], "observer", "source", 1, false, true));
  assert.throws(() => A.perceive([], "observer", "source", 1, 1, false));
} finally { console.error = oldError; }
console.log("Source-scoped visual aversion browser parity passed.");
