"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

load("browser-resources.js");
window.IRON_PIT_BROWSER_GRAPPLE = { speedIsZero: () => false };
window.IRON_PIT_BROWSER_MODIFIERS = { effectiveSpeed: (state) => state.template.speed_ft };
window.IRON_PIT_BROWSER_CONDITION_RULES = { incapacitated: () => false };
load("browser-state.js");

function template(minimum) {
  return {
    id: "test-recharge",
    name: "Test Recharge",
    max_hp: 10,
    speed_ft: 30,
    resources: { breath: 0 },
    resource_recharge: { breath: { maxUses: 1, minimum } },
    traits: [],
  };
}

function fixedDice(values) {
  const rolls = [...values];
  return {
    roll(sides) {
      assert.equal(sides, 6);
      if (!rolls.length) throw new Error("Fixed browser dice sequence exhausted.");
      return rolls.shift();
    },
    remaining: () => rolls.length,
  };
}

const failState = window.IRON_PIT_BROWSER_STATE.buildState(template(5));
window.IRON_PIT_DICE = fixedDice([4]);
assert.deepEqual(window.IRON_PIT_BROWSER_STATE.beginTurn(failState), [
  { id: "breath", roll: 4, restored: false },
]);
assert.equal(failState.resources.breath, 0);

const successState = window.IRON_PIT_BROWSER_STATE.buildState(template(5));
window.IRON_PIT_DICE = fixedDice([5]);
assert.deepEqual(window.IRON_PIT_BROWSER_STATE.beginTurn(successState), [
  { id: "breath", roll: 5, restored: true },
]);
assert.equal(successState.resources.breath, 1);

const rechargeSixState = window.IRON_PIT_BROWSER_STATE.buildState(template(6));
window.IRON_PIT_DICE = fixedDice([6]);
assert.deepEqual(window.IRON_PIT_BROWSER_STATE.beginTurn(rechargeSixState), [
  { id: "breath", roll: 6, restored: true },
]);
assert.equal(rechargeSixState.resources.breath, 1);

const fullState = window.IRON_PIT_BROWSER_STATE.buildState(template(5));
fullState.resources.breath = 1;
const unusedDice = fixedDice([1]);
window.IRON_PIT_DICE = unusedDice;
assert.deepEqual(window.IRON_PIT_BROWSER_STATE.beginTurn(fullState), []);
assert.equal(unusedDice.remaining(), 1, "A full Recharge resource must not consume a d6 roll.");

console.log("Browser universal Recharge 5-6 / Recharge 6 parity regressions passed.");
