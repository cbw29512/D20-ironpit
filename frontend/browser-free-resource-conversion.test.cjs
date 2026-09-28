"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of ["browser-action-economy.js", "browser-resources.js", "browser-resource-conversion.js"]) load(file);

const action = {
  id: "restore-target",
  name: "Restore Target",
  actionCost: "none",
  sourceResourceId: "source",
  sourceCost: 1,
  targetResourceId: "target",
  targetGain: 1,
  targetAllowsOverflow: false,
};
const member = {
  combatant_id: "hero",
  state: {
    template: { name: "Hero", resources: { source: 2, target: 1 }, resource_conversion_actions: [action] },
    resources: { source: 2, target: 0 },
    action_available: true,
    bonus_action_available: true,
    reaction_available: true,
  },
};

const R = window.IRON_PIT_BROWSER_RESOURCE_CONVERSION;
assert.equal(R.available(member.state, action), true);
const event = R.resolve(1, 1, member, action);
assert.equal(member.state.resources.source, 1);
assert.equal(member.state.resources.target, 1);
assert.equal(member.state.action_available, true);
assert.equal(member.state.bonus_action_available, true);
assert.equal(event.feature_id, "restore-target");

console.log("Browser no-action resource conversion regression passed.");
