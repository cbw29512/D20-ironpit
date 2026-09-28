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
load("browser-initiative-resource-refill.js");

function member(current, maximum = 5, grantResourceId = "focus") {
  return {
    combatant_id: "fixture",
    state: {
      template: {
        name: "Fixture",
        resources: { focus: maximum },
        initiative_resource_refill_grants: [{
          source_id: "second-breath",
          source_name: "Second Breath",
          resource_id: grantResourceId,
          when_at_or_below: 0,
          restore_amount: 4,
        }],
      },
      resources: { focus: current },
    },
  };
}

const target = {
  combatant_id: "target",
  state: {
    template: { name: "Target", resources: {}, initiative_resource_refill_grants: [] },
    resources: {},
  },
};

{
  const actor = member(0);
  const result = window.IRON_PIT_BROWSER_INITIATIVE_RESOURCE_REFILL.resolve(
    5, { heroes: [actor], monsters: [target] },
  );
  assert.equal(result.sequence, 6);
  assert.equal(actor.state.resources.focus, 4);
  assert.equal(result.events[0].feature_id, "second-breath");
  assert.match(result.events[0].description, /Second Breath/);
}

{
  const actor = member(1);
  const result = window.IRON_PIT_BROWSER_INITIATIVE_RESOURCE_REFILL.resolve(
    5, { heroes: [actor], monsters: [target] },
  );
  assert.equal(result.sequence, 5);
  assert.deepEqual(result.events, []);
  assert.equal(actor.state.resources.focus, 1);
}

{
  const actor = member(0, 3);
  const result = window.IRON_PIT_BROWSER_INITIATIVE_RESOURCE_REFILL.resolve(
    5, { heroes: [actor], monsters: [target] },
  );
  assert.equal(actor.state.resources.focus, 3);
  assert.equal(result.events[0].resource_remaining, 3);
}

assert.throws(
  () => window.IRON_PIT_BROWSER_INITIATIVE_RESOURCE_REFILL.resolve(
    1, { heroes: [member(0, 5, "missing")], monsters: [target] },
  ),
  /references missing resource missing/,
);



{
  const actor = member(2, 5);
  actor.state.template.resources.gate = 1;
  actor.state.resources.gate = 1;
  actor.state.template.initiative_resource_refill_grants = [{
    source_id: "full-refresh",
    source_name: "Full Refresh",
    resource_id: "focus",
    when_at_or_below: 4,
    restore_amount: 1,
    restore_to_max: true,
    usage_resource_id: "gate",
    usage_resource_cost: 1,
  }];
  let result = window.IRON_PIT_BROWSER_INITIATIVE_RESOURCE_REFILL.resolve(
    9, { heroes: [actor], monsters: [target] },
  );
  assert.equal(result.sequence, 10);
  assert.equal(actor.state.resources.focus, 5);
  assert.equal(actor.state.resources.gate, 0);

  actor.state.resources.focus = 2;
  result = window.IRON_PIT_BROWSER_INITIATIVE_RESOURCE_REFILL.resolve(
    10, { heroes: [actor], monsters: [target] },
  );
  assert.deepEqual(result.events, []);
  assert.equal(actor.state.resources.focus, 2);
}

console.log("Browser initiative resource refill is source-agnostic and fail-closed.");
