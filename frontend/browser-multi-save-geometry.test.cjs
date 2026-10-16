"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const calls = [];
const targetA = { combatant_id: "one", state: {} };
const targetB = { combatant_id: "two", state: {} };
const targets = [targetA, targetB];
const window = {
  IRON_PIT_ACTION_ECONOMY: {
    available: () => true, spend: () => calls.push("action"),
  },
  IRON_PIT_BROWSER_RESOURCES: {
    available: () => true, spend: () => calls.push("resource"),
  },
  IRON_PIT_BROWSER_FORMATION: {
    targetOrder: () => targets, saveDistance: () => 5,
  },
  IRON_PIT_BROWSER_SAVES: {
    legalAction: () => true,
    resolveAction: (_s, _r, _actor, target, _action, _distance, options) => {
      calls.push(target.combatant_id);
      return { target_id: target.combatant_id, shared: options.sharedDamageRolls };
    },
  },
  IRON_PIT_DICE: {
    rollMany: (count, size) => { calls.push("dice:" + size); return [size]; },
  },
};
const source = fs.readFileSync(path.join(__dirname, "browser-multi-save-provider.js"), "utf8");
vm.runInNewContext(source, { window });
const provider = window.IRON_PIT_BROWSER_MULTI_SAVE_PROVIDER;
const member = { combatant_id: "caster", state: { template: { saving_throw_actions: [] } } };
const setup = { heroes: [], monsters: [] };
const area = {
  id: "source", name: "Renamed Area", actionCost: "action", maxTargets: 2,
  range: 30, area: { shape: "cone", origin: "self", length_ft: 15 },
};
member.state.template.saving_throw_actions = [area];
assert.equal(provider.choose(member, setup), null);
assert.throws(() => provider.resolve(1, 1, member, setup, area, targets), /geometry-validated/);
assert.deepEqual(calls, [], "Illegal area targeting must not spend or roll");
const direct = {
  ...area, area: null, name: "Renamed Direct",
  damageComponents: [
    { diceCount: 1, diceSize: 6, damageType: "bludgeoning" },
    { diceCount: 1, diceSize: 8, damageType: "slashing" },
  ],
};
member.state.template.saving_throw_actions = [direct];
assert.equal(provider.choose(member, setup).targets.length, 2);
assert.throws(
  () => provider.resolve(1, 1, member, setup, direct, [targetA, targetA]),
  /unique target IDs/,
);
assert.deepEqual(calls, [], "Duplicate targeting must not spend or roll");
const result = provider.resolve(1, 1, member, setup, direct, targets);
assert.equal(result.events.length, 2);
assert.deepEqual(calls, ["action", "dice:6", "dice:8", "one", "two"]);
assert.deepEqual(Array.from(result.events, (event) => JSON.stringify(event.shared)), [
  "[[6],[8]]", "[[6],[8]]",
]);
console.log("Direct save geometry, uniqueness, and typed shared rolls: PASS");
