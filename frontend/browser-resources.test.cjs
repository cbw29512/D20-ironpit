"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-resources.js"), "utf8"), { filename: "browser-resources.js" });

const R = window.IRON_PIT_BROWSER_RESOURCES;
const action = { id: "fire-breath", resourceId: "breath", resourceCost: 1 };
const state = {
  resources: { breath: 1 },
  template: { kind: "monster", resourceDefinitions: [{ id: "breath", maxUses: 1, rechargeMinimum: 5, rechargeDieSize: 6 }] },
};

assert.equal(R.canUse(state, action), true);
assert.equal(R.spend(state, action), 0);
assert.equal(R.canUse(state, action), false);
assert.throws(() => R.spend(state, action), /unavailable/);

let queue = [4, 5];
window.IRON_PIT_DICE = { roll: () => queue.shift() };
assert.deepEqual(R.refresh(state), [{ resourceId: "breath", roll: 4, recharged: false }]);
assert.equal(state.resources.breath, 0);
assert.deepEqual(R.refresh(state), [{ resourceId: "breath", roll: 5, recharged: true }]);
assert.equal(state.resources.breath, 1);
assert.deepEqual(R.refresh(state), [], "a full recharge resource must not roll again");

console.log("browser action-resource/recharge regression passed");
