"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const calls = [];
let candidateAvailable = true;

window.IRON_PIT_BROWSER_CONDITION_RULES = { incapacitated: () => false };
window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION = {
  discoverCandidates(profileId, ctx) {
    calls.push(["discover", profileId, ctx.sequence, ctx.member.state.action_available]);
    assert.equal(profileId, "actionSurgeAttack");
    return candidateAvailable
      ? [{ providerId: "attack-action", category: "attack-action", opportunityProfile: profileId }]
      : [];
  },
  selectCandidate(profileId, candidates) {
    calls.push(["select", profileId, candidates.length]);
    return candidates[0] || null;
  },
  resolveCandidate(profileId, candidate, ctx) {
    calls.push(["resolve", profileId, candidate.providerId, ctx.sequence, ctx.member.state.action_available]);
    assert.equal(ctx.member.state.action_available, true, "Action Surge must grant the Action before resolution");
    ctx.member.state.action_available = false;
    return {
      events: [{
        sequence: ctx.sequence, round_number: ctx.round, event_type: "attack",
        actor_id: ctx.member.combatant_id, actor_name: ctx.member.state.template.name,
        feature_id: "attack-action", description: "Selector attack resolves.",
      }],
      sequence: ctx.sequence + 1,
    };
  },
};

vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-action-surge.js"), "utf8"),
  { filename: "browser-action-surge.js" },
);

const buildMember = () => ({
  combatant_id: "hero-1",
  state: {
    action_available: false,
    turn_terminated: false,
    is_dead: false,
    is_unconscious: false,
    resources: { "action-surge": 1 },
    feature_last_turn_keys: {},
    template: { name: "Selector Fighter", ruleset: "2024" },
  },
});
const setup = { heroes: [], monsters: [] };

{
  const member = buildMember();
  calls.length = 0;
  const result = window.IRON_PIT_BROWSER_ACTION_SURGE.resolveAttack(5, 2, member, setup, "2:hero-1");
  assert.ok(result);
  assert.deepEqual(calls, [
    ["discover", "actionSurgeAttack", 5, false],
    ["select", "actionSurgeAttack", 1],
    ["resolve", "actionSurgeAttack", "attack-action", 6, true],
  ]);
  assert.deepEqual(result.events.map((event) => event.feature_id), ["action-surge", "attack-action"]);
  assert.equal(result.sequence, 7);
  assert.equal(member.state.resources["action-surge"], 0);
  assert.equal(member.state.action_available, false);
  assert.equal(member.state.feature_last_turn_keys["action-surge"], "2:hero-1");
}

{
  const member = buildMember();
  candidateAvailable = false;
  calls.length = 0;
  const result = window.IRON_PIT_BROWSER_ACTION_SURGE.resolveAttack(10, 3, member, setup, "3:hero-1");
  assert.equal(result, null);
  assert.deepEqual(calls, [
    ["discover", "actionSurgeAttack", 10, false],
    ["select", "actionSurgeAttack", 0],
  ]);
  assert.equal(member.state.resources["action-surge"], 1);
  assert.equal(member.state.action_available, false);
  assert.equal(member.state.feature_last_turn_keys["action-surge"], undefined);
}

const source = fs.readFileSync(path.join(__dirname, "browser-action-surge.js"), "utf8");
assert.match(source, /discoverCandidates\("actionSurgeAttack"/);
assert.doesNotMatch(source, /chooseStandardAttack|resolveAttackAction|BROWSER_STANDARD_ATTACK_ACTION|BROWSER_FORMATION/);

console.log("Browser Action Surge Main Action selector migration passed.");
