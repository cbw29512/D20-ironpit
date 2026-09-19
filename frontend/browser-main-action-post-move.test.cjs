"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

const calls = [];
window.IRON_PIT_BROWSER_STATE = {
  beginTurn() {},
  packTactics: () => false,
};
window.IRON_PIT_BROWSER_CHARGE = {
  resolveClosing: (sequence) => {
    calls.push(["charge", sequence]);
    return { handled: false, events: [], sequence };
  },
};
window.IRON_PIT_BROWSER_RECHARGE = { resolveStartOfTurn: () => null };
window.IRON_PIT_BROWSER_ABILITY_HOOKS = {
  PHASES: { BONUS_ACTION_WINDOW: "bonusActionWindow", TURN_FINALIZE: "turnFinalize" },
  runPhase: (_phase, ctx) => ({ events: [], sequence: ctx.sequence, claimed: false }),
};
window.IRON_PIT_BROWSER_ACTION_SURGE = { resolveAttack: () => null };
window.IRON_PIT_BROWSER_SUPPORT = { resolve: () => null };
window.IRON_PIT_BROWSER_PALADIN_AURAS_2014 = { sync() {} };
window.IRON_PIT_BROWSER_ONGOING_SPELL_CONTROL = { forcedRetreatActive: () => false };
window.IRON_PIT_BROWSER_FORMATION = {
  targetOrder: (_member, setup) => setup.monsters,
};
window.IRON_PIT_BROWSER_OFFENSIVE_MOVEMENT = {
  move: (sequence) => {
    calls.push(["move", sequence]);
    return {
      events: [{ sequence, event_type: "movement", feature_id: "test-movement" }],
      sequence: sequence + 1,
    };
  },
};
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "action" && state.action_available,
};
window.IRON_PIT_BROWSER_GRAPPLE = { cleanup() {}, shouldEscape: () => false };

window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION = {
  discoverCandidates(profileId, ctx) {
    calls.push(["discover", profileId, ctx.sequence]);
    if (profileId === "normalPreMove") return [];
    assert.equal(profileId, "normalPostMove");
    return [{ providerId: "standard-attack", category: "standard-attack" }];
  },
  selectCandidate(profileId, candidates) {
    calls.push(["select", profileId, candidates.length]);
    return candidates[0] || null;
  },
  resolveCandidate(profileId, candidate, ctx) {
    calls.push(["resolve", profileId, candidate.providerId, ctx.sequence]);
    assert.equal(profileId, "normalPostMove");
    ctx.member.state.action_available = false;
    return {
      events: [{
        sequence: ctx.sequence,
        round_number: ctx.round,
        event_type: "attack",
        actor_id: ctx.member.combatant_id,
        actor_name: ctx.member.state.template.name,
        feature_id: "selector-post-move",
        description: "Post-move Main Action resolves through selector.",
      }],
      sequence: ctx.sequence + 1,
    };
  },
};

load("browser-turn.js");

const member = {
  combatant_id: "hero-1",
  side: "heroes",
  position_ft: 0,
  state: {
    action_available: true,
    bonus_action_available: true,
    template: { name: "Post Move Tester", ruleset: "2024" },
  },
};
const setup = {
  heroes: [member],
  monsters: [{
    combatant_id: "monster-1",
    side: "monsters",
    position_ft: 10,
    state: { template: { name: "Target", ruleset: "2024" } },
  }],
};

const result = window.IRON_PIT_BROWSER_TURN.resolveTurn(1, 2, member, setup);

assert.deepEqual(calls, [
  ["discover", "normalPreMove", 1],
  ["select", "normalPreMove", 0],
  ["charge", 1],
  ["move", 1],
  ["discover", "normalPostMove", 2],
  ["select", "normalPostMove", 1],
  ["resolve", "normalPostMove", "standard-attack", 2],
]);
assert.equal(result.sequence, 3);
assert.deepEqual(result.events.map((event) => event.feature_id), [
  "test-movement",
  "selector-post-move",
]);
assert.equal(member.state.action_available, false);

const turnSource = fs.readFileSync(path.join(__dirname, "browser-turn.js"), "utf8");
assert.match(turnSource, /resolveMainActionOpportunity\("normalPostMove"/);
for (const forbidden of [
  "const movedSpell =",
  "const presence = IP()?.resolve",
  "M().resolveAttackAction",
  "const area = AS()?.resolve",
  "const saved = saveChoice",
  "const standard = U().resolve",
  "DG().take",
]) {
  assert.equal(turnSource.includes(forbidden), false, "legacy named post-move Action branch remains: " + forbidden);
}

console.log("Browser normalPostMove Main Action selector migration passed.");
