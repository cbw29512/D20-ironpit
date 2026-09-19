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
let selectorHasCandidate = true;
let chargeCalls = 0;
window.IRON_PIT_BROWSER_STATE = {
  beginTurn() {},
  packTactics: () => false,
};
window.IRON_PIT_BROWSER_CHARGE = {
  resolveClosing: (sequence) => {
    chargeCalls += 1;
    return selectorHasCandidate ? (() => { throw new Error("movement/charge must not run after pre-move spell consumes Action"); })() : { handled: true, events: [{ sequence, event_type: "feature", feature_id: "charge" }], sequence: sequence + 1 };
  },
};
window.IRON_PIT_BROWSER_RECHARGE = { resolveStartOfTurn: () => null };
window.IRON_PIT_BROWSER_MULTIATTACK = {};
window.IRON_PIT_BROWSER_ABILITY_HOOKS = {
  PHASES: { BONUS_ACTION_WINDOW: "bonusActionWindow", TURN_FINALIZE: "turnFinalize" },
  runPhase: (_phase, ctx) => ({ events: [], sequence: ctx.sequence, claimed: false }),
};
window.IRON_PIT_BROWSER_ACTION_SURGE = { resolveAttack: () => null };
window.IRON_PIT_BROWSER_SUPPORT = { resolve: () => null };
window.IRON_PIT_BROWSER_INTIMIDATING_PRESENCE_2014 = {};
window.IRON_PIT_BROWSER_PALADIN_AURAS_2014 = { sync() {} };
window.IRON_PIT_BROWSER_ONGOING_SPELL_CONTROL = { forcedRetreatActive: () => false };
window.IRON_PIT_BROWSER_SPELL_OFFENSE = {
  resolve: () => { throw new Error("legacy direct pre-move spell path must not execute"); },
};
window.IRON_PIT_BROWSER_FORMATION = {
  targetOrder: () => { throw new Error("targeting must not run after pre-move spell consumes Action"); },
};
window.IRON_PIT_BROWSER_SAVES = {};
window.IRON_PIT_BROWSER_AREA_SAVES = {};
window.IRON_PIT_BROWSER_DODGE = {};
window.IRON_PIT_BROWSER_OFFENSIVE_MOVEMENT = {
  move: () => { throw new Error("movement must not run after pre-move spell consumes Action"); },
};
window.IRON_PIT_DICE = {};
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "action" && state.action_available,
};
window.IRON_PIT_BROWSER_GRAPPLE = { cleanup() {}, shouldEscape: () => false };

window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION = {
  discoverCandidates(profileId, ctx) {
    calls.push(["discover", profileId, ctx.sequence, ctx.turnKey]);
    assert.equal(profileId, "normalPreMove");
    return selectorHasCandidate ? [{ providerId: "spell-offense", category: "spell-offense" }] : [];
  },
  selectCandidate(profileId, candidates) {
    calls.push(["select", profileId, candidates.length]);
    return candidates[0] || null;
  },
  resolveCandidate(profileId, candidate, ctx) {
    calls.push(["resolve", profileId, candidate.providerId, ctx.sequence]);
    ctx.member.state.action_available = false;
    return {
      events: [{
        sequence: ctx.sequence, round_number: ctx.round, event_type: "attack",
        actor_id: ctx.member.combatant_id, actor_name: ctx.member.state.template.name,
        feature_id: "test-spell", description: "Pre-move spell resolves through selector.",
      }],
      sequence: ctx.sequence + 1,
    };
  },
};

load("browser-turn.js");

const member = {
  combatant_id: "hero-1", side: "heroes",
  state: {
    action_available: true, bonus_action_available: true,
    template: { name: "Selector Caster", ruleset: "2024" },
  },
};
const setup = { heroes: [member], monsters: [{ combatant_id: "monster-1", side: "monsters", state: { template: { name: "Target" } } }] };

const result = window.IRON_PIT_BROWSER_TURN.resolveTurn(1, 2, member, setup);

assert.deepEqual(calls, [
  ["discover", "normalPreMove", 1, "2:hero-1"],
  ["select", "normalPreMove", 1],
  ["resolve", "normalPreMove", "spell-offense", 1],
]);
assert.equal(result.sequence, 2);
assert.equal(result.events.length, 1);
assert.equal(result.events[0].feature_id, "test-spell");
assert.equal(member.state.action_available, false);
assert.equal(chargeCalls, 0);

selectorHasCandidate = false;
calls.length = 0;
chargeCalls = 0;
member.state.action_available = true;
const passthrough = window.IRON_PIT_BROWSER_TURN.resolveTurn(10, 3, member, setup);
assert.deepEqual(calls, [
  ["discover", "normalPreMove", 10, "3:hero-1"],
  ["select", "normalPreMove", 0],
]);
assert.equal(chargeCalls, 1);
assert.equal(passthrough.events.some((event) => event.feature_id === "charge"), true);
assert.equal(member.state.action_available, true);

const turnSource = fs.readFileSync(path.join(__dirname, "browser-turn.js"), "utf8");
assert.match(turnSource, /resolveMainActionOpportunity\("normalPreMove"/);
assert.doesNotMatch(turnSource, /const spell = L\(\)\?\.resolve\(sequence, round, member, setup, turnKey\)/);

console.log("Browser normalPreMove Main Action selector migration passed.");
