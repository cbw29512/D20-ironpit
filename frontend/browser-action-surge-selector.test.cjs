"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

window.IRON_PIT_BROWSER_CONDITION_RULES = { incapacitated: () => false };

load("browser-action-surge.js");

function actor() {
  return {
    combatant_id: "hero-1",
    side: "heroes",
    state: {
      action_available: false,
      turn_terminated: false,
      is_dead: false,
      is_unconscious: false,
      resources: { "action-surge": 1 },
      feature_last_turn_keys: {},
      template: { name: "Selector Fighter", ruleset: "2024" },
    },
  };
}

{
  const member = actor();
  const calls = [];
  window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION = {
    discoverCandidates(profileId, ctx) {
      calls.push(["discover", profileId, ctx.sequence, ctx.member.state.action_available]);
      return [];
    },
    selectCandidate(profileId, candidates) {
      calls.push(["select", profileId, candidates.length]);
      return null;
    },
    resolveCandidate() {
      throw new Error("resolution must not run without a candidate");
    },
  };

  const result = window.IRON_PIT_BROWSER_ACTION_SURGE.resolveAttack(
    5, 2, member, { heroes: [member], monsters: [] }, "2:hero-1",
  );

  assert.equal(result, null);
  assert.equal(member.state.resources["action-surge"], 1, "no candidate must not spend Action Surge");
  assert.equal(member.state.action_available, false);
  assert.equal(member.state.feature_last_turn_keys["action-surge"], undefined);
  assert.deepEqual(calls, [
    ["discover", "actionSurgeAttack", 5, false],
    ["select", "actionSurgeAttack", 0],
  ]);
}

{
  const member = actor();
  const calls = [];
  const candidate = {
    providerId: "attack-action",
    category: "attack-action",
    opportunityProfile: "actionSurgeAttack",
    combatantId: "hero-1",
    turnKey: "2:hero-1",
    payload: {},
  };
  window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION = {
    discoverCandidates(profileId, ctx) {
      calls.push(["discover", profileId, ctx.sequence, ctx.member.state.action_available]);
      return [candidate];
    },
    selectCandidate(profileId, candidates) {
      calls.push(["select", profileId, candidates.length]);
      return candidates[0];
    },
    resolveCandidate(profileId, selected, ctx) {
      calls.push(["resolve", profileId, selected.providerId, ctx.sequence, ctx.member.state.action_available]);
      assert.equal(ctx.member.state.action_available, true, "Surge must grant Action before selected attack resolves");
      ctx.member.state.action_available = false;
      return {
        events: [{
          sequence: ctx.sequence,
          round_number: ctx.round,
          event_type: "attack",
          actor_id: ctx.member.combatant_id,
          actor_name: ctx.member.state.template.name,
          feature_id: "attack-action",
          description: "Selected Action Surge attack resolves.",
        }],
        sequence: ctx.sequence + 1,
      };
    },
  };

  const result = window.IRON_PIT_BROWSER_ACTION_SURGE.resolveAttack(
    10, 2, member, { heroes: [member], monsters: [] }, "2:hero-1",
  );

  assert.ok(result);
  assert.equal(result.sequence, 12);
  assert.equal(result.events.length, 2);
  assert.equal(result.events[0].feature_id, "action-surge");
  assert.equal(result.events[1].feature_id, "attack-action");
  assert.equal(member.state.resources["action-surge"], 0);
  assert.equal(member.state.action_available, false);
  assert.equal(member.state.feature_last_turn_keys["action-surge"], "2:hero-1");
  assert.deepEqual(calls, [
    ["discover", "actionSurgeAttack", 10, false],
    ["select", "actionSurgeAttack", 1],
    ["resolve", "actionSurgeAttack", "attack-action", 11, true],
  ]);
}

console.log("Browser Action Surge Main Action selector reuse passed.");
