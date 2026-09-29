"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-initiative-resource-refill.js"), "utf8"),
  { filename: "browser-initiative-resource-refill.js" },
);

function member(uses) {
  return {
    combatant_id: "lyra-18",
    side: "heroes",
    state: {
      template: {
        name: "Lyra Silverstring",
        resources: { "bardic-inspiration": 5 },
        initiative_resource_refill_grants: [{
          source_id: "superior-inspiration",
          source_name: "Superior Inspiration",
          resource_id: "bardic-inspiration",
          when_at_or_below: 1,
          restore_amount: 1,
          restore_to_max: false,
          restore_to_minimum: 2,
          usage_resource_id: null,
          usage_resource_cost: 1,
        }],
      },
      resources: { "bardic-inspiration": uses },
    },
  };
}

const R = window.IRON_PIT_BROWSER_INITIATIVE_RESOURCE_REFILL;

for (const [before, after, events] of [[0, 2, 1], [1, 2, 1], [2, 2, 0]]) {
  const lyra = member(before);
  const result = R.resolve(1, { heroes: [lyra], monsters: [] });
  assert.equal(lyra.state.resources["bardic-inspiration"], after);
  assert.equal(result.events.length, events);
}

console.log("2024 Superior Inspiration browser regression passed.");
