"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "action" && state.action_available,
};
window.IRON_PIT_BROWSER_FORMATION = {
  targetOrder: (_member, setup) => setup.monsters,
  saveDistance: () => 5,
  chooseStandardAttack: (_member, setup) => ({
    target: setup.monsters[0], attack: { id: "sword" }, distance: 5,
  }),
};
window.IRON_PIT_BROWSER_INTIMIDATING_PRESENCE_2014 = {
  canUse: (member) => member.state.template.ruleset === "2014",
  resolve: (sequence, round, member, target) => ({
    sequence, round_number: round, event_type: "saving_throw",
    actor_id: member.combatant_id, target_id: target.combatant_id,
  }),
};
window.IRON_PIT_BROWSER_MULTIATTACK = {
  available: () => true,
  resolveAttackAction: (sequence) => ({ events: [{ event_type: "attack" }], sequence: sequence + 1 }),
};
window.IRON_PIT_BROWSER_AREA_SAVES = {
  choose: () => ({ action: { id: "breath" }, placement: { targetIds: ["monster-1"] } }),
  resolve: (sequence) => ({ events: [{ event_type: "saving_throw" }], sequence: sequence + 1 }),
};
window.IRON_PIT_BROWSER_SAVE_ACTION_POLICY = {
  choose: (_member, setup) => ({ target: setup.monsters[0], action: { id: "save" }, distance: 5 }),
};
window.IRON_PIT_BROWSER_SAVES = {
  resolveAction: (sequence) => ({ sequence, event_type: "saving_throw" }),
};
window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION = {
  resolve: (sequence) => ({ events: [{ event_type: "attack" }], sequence: sequence + 1 }),
};
window.IRON_PIT_BROWSER_DODGE = {
  take: (sequence) => ({ sequence, event_type: "feature" }),
};
window.IRON_PIT_BROWSER_STATE = { packTactics: () => false };
window.IRON_PIT_BROWSER_CHARGE = { openingFeature: () => null };
window.IRON_PIT_BROWSER_SPELL_OFFENSE = {
  choose: (member) => member.state.action_available
    ? { kind: "attack", choice: { action: { id: "bolt" } } } : null,
  resolveChoice: (sequence) => ({ events: [{ event_type: "attack" }], sequence: sequence + 1 }),
};

load("browser-main-action-profiles.js");
load("browser-main-action-selection.js");
load("browser-main-action-spell-provider.js");
load("browser-main-action-core-providers.js");

const S = window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION;
const member = (ruleset = "2024") => ({
  combatant_id: "hero-1",
  state: { template: { ruleset }, action_available: true },
});
const target = {
  combatant_id: "monster-1",
  state: { template: { ruleset: "2024" }, is_alive: true, is_dead: false },
};
const ctx = (ruleset = "2024") => ({
  sequence: 10, round: 2, turnKey: "2:hero-1",
  member: member(ruleset), setup: { heroes: [], monsters: [target] },
});

{
  const context = ctx();
  const before = structuredClone(context);
  const candidates = S.discoverCandidates("normalPreMove", context);
  assert.deepEqual(candidates.map((item) => item.category), ["spell-offense"]);
  assert.equal(S.selectCandidate("normalPreMove", candidates).providerId, "spell-offense");
  assert.deepEqual(context, before, "discovery must not mutate context state");
}

{
  const candidates = S.discoverCandidates("normalPostMove", ctx());
  assert.deepEqual(
    candidates.map((item) => item.category),
    ["spell-offense", "attack-action", "area-save", "save-action", "standard-attack", "dodge"],
  );
  assert.equal(S.selectCandidate("normalPostMove", candidates).providerId, "spell-offense");
}

{
  const candidates = S.discoverCandidates("actionSurgeAttack", ctx());
  assert.deepEqual(candidates.map((item) => item.category), ["attack-action", "standard-attack"]);
  assert.equal(S.selectCandidate("actionSurgeAttack", candidates).providerId, "attack-action");
}


{
  const context = ctx();
  context.member.state.action_available = false;
  const candidates = S.discoverCandidates("normalPostMove", context);
  assert.deepEqual(candidates, [], "spent Action must suppress all Main Action candidates");
}

{
  const savedSpell = window.IRON_PIT_BROWSER_SPELL_OFFENSE.choose;
  window.IRON_PIT_BROWSER_SPELL_OFFENSE.choose = () => null;
  const candidates = S.discoverCandidates("normalPostMove", ctx("2014"));
  assert.deepEqual(
    candidates.map((item) => item.category),
    ["intimidating-presence-2014", "attack-action", "area-save", "save-action", "standard-attack", "dodge"],
  );
  assert.equal(S.selectCandidate("normalPostMove", candidates).providerId, "intimidating-presence-2014");
  window.IRON_PIT_BROWSER_SPELL_OFFENSE.choose = savedSpell;
}

{
  const selected = S.selectCandidate("actionSurgeAttack", S.discoverCandidates("actionSurgeAttack", ctx()));
  const result = S.resolveCandidate("actionSurgeAttack", selected, ctx());
  assert.equal(result.sequence, 11);
  assert.deepEqual(result.events.map((event) => event.event_type), ["attack"]);
}

console.log("Browser Main Action provider discovery regressions passed.");
