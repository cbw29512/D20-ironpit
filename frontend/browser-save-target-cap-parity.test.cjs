"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

// Exercise the real browser resolver with source-neutral synthetic cards.
const source = fs.readFileSync(path.join(__dirname, "browser-multi-save-provider.js"), "utf8");
const calls = [];
const window = {
  IRON_PIT_ACTION_ECONOMY: {
    available: () => true,
    spend: () => calls.push("action-spent"),
  },
  IRON_PIT_BROWSER_RESOURCES: { available: () => true, spend: () => null },
  IRON_PIT_BROWSER_FORMATION: { saveDistance: () => 5 },
  IRON_PIT_BROWSER_SAVES: {
    legalAction: () => true,
    resolveAction: (_sequence, _round, _actor, target) => {
      calls.push(target.combatant_id);
      return { target_id: target.combatant_id };
    },
  },
};
vm.runInNewContext(source, { window });
const provider = window.IRON_PIT_BROWSER_MULTI_SAVE_PROVIDER;
const member = { state: {} };
const setup = { heroes: [], monsters: [] };
const targets = [{ combatant_id: "one" }, { combatant_id: "two" }];
const action = {
  id: "synthetic-save", name: "Renamed Homebrew Action", range: 30,
  maxTargets: 1, actionCost: "action",
};
assert.throws(
  () => provider.resolve(1, 1, member, setup, action, targets),
  /declared target cap/,
);
assert.deepEqual(calls, [], "Over-cap actions cannot spend resources or resolve saves");
assert.throws(
  () => provider.resolve(1, 1, member, setup, { ...action, maxTargets: 2 },
    [targets[0], targets[0]]),
  /unique target IDs/,
);
assert.deepEqual(calls, [], "Duplicate targets cannot spend resources or take repeated damage");
const accepted = provider.resolve(1, 1, member, setup, { ...action, maxTargets: 2 }, targets);
assert.equal(accepted.events.length, 2);
assert.deepEqual(calls, ["action-spent", "one", "two"]);
console.log("Browser source-card save target caps passed.");
