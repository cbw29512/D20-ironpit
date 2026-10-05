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
load("browser-action-economy.js");
load("browser-delayed-resource-refill.js");

function makeMember() {
  return {
    combatant_id: "varek",
    side: "heroes",
    state: {
      template: {
        name: "Varek Ashenmark",
        ruleset: "2024",
        resources: { "spell-slot-1": 2, "magical-cunning": 1 },
        delayed_resource_refill: {
          source_id: "magical-cunning",
          source_name: "Magical Cunning",
          resource_ids: ["spell-slot-1"],
          use_resource_id: "magical-cunning",
          use_resource_cost: 1,
          delay_rounds: 10,
          restore_mode: "half_max_rounded_up",
        },
      },
      resources: { "spell-slot-1": 0, "magical-cunning": 1 },
      delayed_resource_refills: [],
      action_available: true,
      bonus_action_available: true,
      reaction_available: true,
      movement_remaining_ft: 30,
      is_dead: false,
      is_unconscious: false,
      timed_effects: [],
    },
  };
}

const H = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
const R = window.IRON_PIT_BROWSER_DELAYED_RESOURCE_REFILL;
const E = window.IRON_PIT_ACTION_ECONOMY;
R.installAbilityHooks();

const idle = makeMember();
let result = H.runPhase(H.PHASES.TURN_END_LIFECYCLE, {
  sequence: 1, round: 1, member: idle, setup: { heroes: [idle], monsters: [] }, events: [],
});
assert.equal(result.events.length, 0);
assert.equal(idle.state.resources["magical-cunning"], 1);
assert.equal(idle.state.delayed_resource_refills.length, 0);

const member = makeMember();
result = R.start({ sequence: 1, round: 1, member });
assert.equal(result.events[0].feature_id, "magical-cunning");
assert.equal(member.state.resources["magical-cunning"], 0);
assert.equal(member.state.resources["spell-slot-1"], 0);
assert.equal(E.available(member.state, "action"), false);
assert.equal(E.available(member.state, "bonus_action"), false);
assert.equal(E.available(member.state, "reaction"), true);
assert.equal(member.state.movement_remaining_ft, 0);

member.state.current_hp = 12;
result = H.runPhase(H.PHASES.TURN_END_LIFECYCLE, {
  sequence: result.sequence, round: 4, member, setup: { heroes: [member], monsters: [] }, events: [],
});
assert.equal(result.events.length, 0);
assert.equal(member.state.resources["spell-slot-1"], 0);

for (let round = 5; round < 11; round += 1) {
  result = H.runPhase(H.PHASES.TURN_END_LIFECYCLE, {
    sequence: result.sequence, round, member, setup: { heroes: [member], monsters: [] }, events: [],
  });
  assert.equal(result.events.length, 0);
}

result = H.runPhase(H.PHASES.TURN_END_LIFECYCLE, {
  sequence: result.sequence, round: 11, member, setup: { heroes: [member], monsters: [] }, events: [],
});
assert.equal(result.events.length, 1);
assert.match(result.events[0].description, /completes Magical Cunning/);
assert.equal(member.state.resources["spell-slot-1"], 1);
assert.equal(member.state.delayed_resource_refills.length, 0);

const stopped = makeMember();
R.start({ sequence: 1, round: 1, member: stopped });
stopped.state.is_unconscious = true;
result = H.runPhase(H.PHASES.TURN_END_LIFECYCLE, {
  sequence: 2, round: 4, member: stopped, setup: { heroes: [stopped], monsters: [] }, events: [],
});
assert.match(result.events[0].description, /stops Magical Cunning/);
assert.equal(stopped.state.resources["spell-slot-1"], 0);
assert.equal(stopped.state.delayed_resource_refills.length, 0);

console.log("2024 Magical Cunning committed rite browser regression passed.");
