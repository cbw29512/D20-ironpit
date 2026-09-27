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

load("browser-ability-hooks.js");
load("browser-delayed-resource-refill.js");

const member = {
  combatant_id: "varek",
  side: "heroes",
  state: {
    template: {
      name: "Varek Ashenmark",
      ruleset: "2014",
      resources: { "spell-slot-5": 4, "eldritch-master": 1 },
      delayed_resource_refill: {
        source_id: "eldritch-master",
        source_name: "Eldritch Master",
        resource_ids: ["spell-slot-5"],
        use_resource_id: "eldritch-master",
        use_resource_cost: 1,
        delay_rounds: 10,
      },
    },
    resources: { "spell-slot-5": 1, "eldritch-master": 1 },
    delayed_resource_refills: [],
  },
};
const setup = { heroes: [member], monsters: [] };
const H = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
window.IRON_PIT_BROWSER_DELAYED_RESOURCE_REFILL.installAbilityHooks();

let result = H.runPhase(H.PHASES.TURN_END_LIFECYCLE, {
  sequence: 1, round: 1, member, setup, events: [],
});
assert.equal(result.events.length, 1);
assert.equal(result.events[0].feature_id, "eldritch-master");
assert.equal(member.state.resources["eldritch-master"], 0);
assert.equal(member.state.resources["spell-slot-5"], 1);
assert.equal(member.state.delayed_resource_refills[0].completes_round, 11);

for (let round = 2; round < 11; round += 1) {
  result = H.runPhase(H.PHASES.TURN_END_LIFECYCLE, {
    sequence: result.sequence, round, member, setup, events: [],
  });
  assert.equal(result.events.length, 0);
  assert.equal(member.state.resources["spell-slot-5"], 1);
}

result = H.runPhase(H.PHASES.TURN_END_LIFECYCLE, {
  sequence: result.sequence, round: 11, member, setup, events: [],
});
assert.equal(result.events.length, 1);
assert.equal(member.state.resources["spell-slot-5"], 4);
assert.equal(member.state.delayed_resource_refills.length, 0);

member.state.resources["spell-slot-5"] = 0;
result = H.runPhase(H.PHASES.TURN_END_LIFECYCLE, {
  sequence: result.sequence, round: 12, member, setup, events: [],
});
assert.equal(result.events.length, 0);
assert.equal(member.state.delayed_resource_refills.length, 0);

console.log("2014 Eldritch Master delayed Pact refill browser regression passed.");
