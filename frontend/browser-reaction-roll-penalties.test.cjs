"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = {};
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "reaction" && state.reaction_available,
  spend: (state, cost) => {
    if (cost !== "reaction" || !state.reaction_available) throw new Error("Reaction unavailable.");
    state.reaction_available = false;
  },
};
window.IRON_PIT_DICE = { roll: () => 3 };
window.IRON_PIT_BROWSER_STATE = { distance: (a, b) => Math.abs(a.position_ft - b.position_ft) };
window.IRON_PIT_BROWSER_CONDITION_RULES = {
  has: (state, id) => (state.active_effect_ids || []).includes(id),
};
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = {
  immune: (state, id) => (state.template.condition_immunities || []).includes(id),
};

vm.runInThisContext(fs.readFileSync("frontend/browser-reaction-roll-penalties.js", "utf8"));

const action = {
  id: "test-penalty", name: "Test Penalty", range: 60,
  resourceId: "penalty-use", resourceCost: 1, diceCount: 1, diceSize: 8,
  rollKinds: ["attack", "ability_check", "damage"], requiresSourceSight: true,
  requiresTargetHearing: true, blockedTargetConditionImmunity: "charmed", priority: 20,
};
const reactor = {
  combatant_id: "reactor", side: "heroes", position_ft: 0,
  state: {
    reaction_available: true, resources: { "penalty-use": 2 }, active_effect_ids: [],
    template: { name: "Reactor", condition_immunities: [], reactionRollPenaltyActions: [action] },
  },
};
const roller = {
  combatant_id: "roller", side: "monsters", position_ft: 20,
  state: {
    reaction_available: true, resources: {}, active_effect_ids: [],
    template: { name: "Roller", condition_immunities: [], reactionRollPenaltyActions: [] },
  },
};
const setup = { heroes: [reactor], monsters: [roller] };
const P = window.IRON_PIT_BROWSER_REACTION_ROLL_PENALTIES;
const roll = {
  notation: "1d20+4", rolls: [12], selected_roll: 12,
  modifier: 4, total: 16, mode: "normal", revisions: [],
};

const result = P.applyIfUseful(roller, setup, "attack", roll, 15);
assert.ok(result);
assert.equal(result.roll.total, 13);
assert.equal(result.roll.revisions.at(-1).kind, "roll_penalty");
assert.equal(reactor.state.reaction_available, false);
assert.equal(reactor.state.resources["penalty-use"], 1);

reactor.state.reaction_available = true;
reactor.state.resources["penalty-use"] = 2;
assert.equal(P.applyIfUseful(roller, setup, "attack", { ...roll, total: 25 }, 15), null);
assert.equal(reactor.state.reaction_available, true);

roller.state.active_effect_ids = ["deafened"];
assert.equal(P.applyIfUseful(roller, setup, "attack", roll, 15), null);
roller.state.active_effect_ids = [];

reactor.state.active_effect_ids = ["blinded"];
assert.equal(P.applyIfUseful(roller, setup, "attack", roll, 15), null);

console.log("Browser reaction roll-penalty regressions passed.");
