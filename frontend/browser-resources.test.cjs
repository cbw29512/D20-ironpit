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
  template: {
    kind: "monster", name: "Test Dragon",
    resourceDefinitions: [{ id: "breath", name: "Breath Weapon", maxUses: 1, rechargeMinimum: 5, rechargeDieSize: 6 }],
  },
};

assert.equal(R.canUse(state, action), true);
assert.equal(R.spend(state, action), 0);
assert.equal(R.canUse(state, action), false);
assert.throws(() => R.spend(state, action), /unavailable/);

let queue = [4, 5];
window.IRON_PIT_DICE = { roll: () => queue.shift() };
assert.deepEqual(R.refresh(state), [{ resourceId: "breath", roll: 4, recharged: false }]);
assert.equal(state.resources.breath, 0);
const success = R.refresh(state);
assert.deepEqual(success, [{ resourceId: "breath", roll: 5, recharged: true }]);
assert.equal(state.resources.breath, 1);
assert.deepEqual(R.refresh(state), [], "a full recharge resource must not roll again");

const member = { combatant_id: "monster-1", state };
const audit = R.buildRechargeEvents(state, member, 2, 7, success);
assert.equal(audit.sequence, 8);
assert.equal(audit.events.length, 1);
assert.equal(audit.events[0].feature_id, "breath");
assert.equal(audit.events[0].resource_remaining, 1);
assert.match(audit.events[0].description, /d6: 5 vs 5\+; recharged to 1/);
assert.deepEqual(audit.events[0].audit.steps.map((step) => step.phase), ["roll", "resource_change"]);

console.log("browser action-resource/recharge regression passed");