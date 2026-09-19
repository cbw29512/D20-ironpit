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
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "action" && state.action_available,
};
window.IRON_PIT_BROWSER_FORMATION = {
  targetOrder: (_member, setup) => [setup.monsters[0]],
  saveDistance: () => 5,
  chooseStandardAttack: (member, setup) => {
    calls.push("standard-discover");
    return member.state.template.standardEnabled
      ? { target: setup.monsters[0], attack: member.state.template.attacks[0], distance: 5 }
      : null;
  },
};
window.IRON_PIT_BROWSER_SPELL_OFFENSE = {
  choose: (member) => {
    calls.push("spell-discover");
    return member.state.template.spellEnabled
      ? { kind: "attack", choice: { action: { id: "spell" }, target: null } }
      : null;
  },
  resolveChoice: (sequence) => ({ events: [{ event_type: "attack", feature_id: "spell" }], sequence: sequence + 1 }),
};
window.IRON_PIT_BROWSER_INTIMIDATING_PRESENCE_2014 = {
  canUse: (member) => {
    calls.push("presence-discover");
    return Boolean(member.state.template.presenceEnabled);
  },
  resolve: (sequence) => ({ sequence, event_type: "saving_throw", feature_id: "intimidating-presence-2014" }),
};
window.IRON_PIT_BROWSER_MULTIATTACK = {
  available: (member) => {
    calls.push("attack-discover");
    return Boolean(member.state.template.attackActionEnabled);
  },
  resolveAttackAction: (sequence) => ({ events: [{ event_type: "attack", feature_id: "attack-action" }], sequence: sequence + 1 }),
};
window.IRON_PIT_BROWSER_AREA_SAVES = {
  choose: (member) => {
    calls.push("area-discover");
    return member.state.template.areaEnabled ? { action: { id: "area" }, placement: { targetIds: ["monster-1"] } } : null;
  },
  resolve: (sequence) => ({ events: [{ event_type: "saving_throw", feature_id: "area" }], sequence: sequence + 1 }),
};
window.IRON_PIT_BROWSER_SAVES = {
  legalAction: () => true,
  resolveAction: (sequence) => ({ sequence, event_type: "saving_throw", feature_id: "save-action" }),
};
window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION = {
  resolve: (sequence, _round, _member, _target, _attack, _distance, _setup, _turnKey, options) => ({
    events: [{ event_type: "attack", feature_id: options.featureId || "standard-attack" }],
    sequence: sequence + 1,
  }),
};
window.IRON_PIT_BROWSER_DODGE = {
  take: (sequence) => ({ sequence, event_type: "feature", feature_id: "dodge" }),
};
window.IRON_PIT_BROWSER_STATE = { packTactics: () => false };
window.IRON_PIT_BROWSER_CHARGE = { openingFeature: () => null };

load("browser-main-action-profiles.js");
load("browser-main-action-selection.js");
load("browser-main-action-providers.js");

const S = window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION;
const target = {
  combatant_id: "monster-1", side: "monsters",
  state: { template: { ruleset: "2024" }, is_alive: true, is_dead: false, current_hp: 20 },
};
const member = (ruleset = "2024") => ({
  combatant_id: `hero-${ruleset}`, side: "heroes",
  state: {
    action_available: true,
    template: {
      ruleset, spellEnabled: true, presenceEnabled: true, attackActionEnabled: true,
      intimidating_presence_2014_dc: ruleset === "2014" ? 15 : 0,
      areaEnabled: true, standardEnabled: true,
      attacks: [{ id: "sword" }],
      saving_throw_actions: [{ id: "save", range: 30 }],
    },
  },
});
const ctx = (actor) => ({
  sequence: 3, round: 1, turnKey: `1:${actor.combatant_id}`,
  member: actor, setup: { heroes: [actor], monsters: [target] },
});

{
  const actor = member("2024");
  const before = JSON.stringify(actor.state);
  calls.length = 0;
  const candidates = S.discoverCandidates("normalPreMove", ctx(actor));
  assert.equal(JSON.stringify(actor.state), before, "Main Action discovery must not mutate combat state");
  assert.deepEqual(candidates.map((item) => item.providerId), ["spell-offense"]);
  assert.deepEqual(calls, ["spell-discover"], "normalPreMove must not discover disallowed categories");
}

{
  const actor = member("2024");
  calls.length = 0;
  const candidates = S.discoverCandidates("normalPostMove", ctx(actor));
  assert.deepEqual(
    candidates.map((item) => item.providerId),
    ["spell-offense", "attack-action", "area-save", "save-action", "standard-attack", "dodge"],
  );
  assert.equal(candidates.some((item) => item.providerId === "intimidating-presence-2014"), false);
  assert.equal(S.selectCandidate("normalPostMove", candidates).providerId, "spell-offense");
}

{
  const actor = member("2014");
  const candidates = S.discoverCandidates("normalPostMove", ctx(actor));
  assert.equal(candidates.some((item) => item.providerId === "intimidating-presence-2014"), true);
}

{
  const actor = member("2024");
  calls.length = 0;
  const candidates = S.discoverCandidates("actionSurgeAttack", ctx(actor));
  assert.deepEqual(candidates.map((item) => item.providerId), ["attack-action", "standard-attack"]);
  assert.deepEqual(calls, ["attack-discover", "standard-discover"]);
  assert.equal(S.selectCandidate("actionSurgeAttack", candidates).providerId, "attack-action");
}

{
  const actor = member("2024");
  actor.state.template.attackActionEnabled = false;
  const candidates = S.discoverCandidates("actionSurgeAttack", ctx(actor));
  const selected = S.selectCandidate("actionSurgeAttack", candidates);
  assert.equal(selected.providerId, "standard-attack");
  const resolved = S.resolveCandidate("actionSurgeAttack", selected, ctx(actor));
  assert.equal(resolved.events[0].feature_id, "action-surge");
}

{
  const actor = member("2024");
  actor.state.template.spellEnabled = false;
  actor.state.template.attackActionEnabled = false;
  actor.state.template.areaEnabled = false;
  actor.state.template.standardEnabled = false;
  actor.state.template.saving_throw_actions = [];
  const selected = S.selectCandidate("normalPostMove", S.discoverCandidates("normalPostMove", ctx(actor)));
  assert.equal(selected.providerId, "dodge");
  const resolved = S.resolveCandidate("normalPostMove", selected, ctx(actor));
  assert.equal(resolved.events[0].feature_id, "dodge");
}

console.log("Browser Main Action provider registration/discovery parity passed.");
