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

window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "action" && state.action_available,
};
window.IRON_PIT_BROWSER_FORMATION = {
  targetOrder: (_member, setup) => setup.monsters,
  chooseStandardAttack: () => null,
  saveDistance: () => 5,
};
window.IRON_PIT_BROWSER_SPELL_OFFENSE = {
  choose: () => null,
  resolveChoice: (sequence) => ({ events: [], sequence }),
};
window.IRON_PIT_BROWSER_MULTIATTACK = {
  available: () => true,
  legalChoiceAvailable: () => true,
  resolveAttackAction: (sequence) => ({
    events: [{ event_type: "attack", feature_id: "multiattack" }],
    sequence: sequence + 1,
  }),
};
window.IRON_PIT_BROWSER_AREA_SAVES = {
  choose: (_member, _setup, resourceOnly) => resourceOnly
    ? { action: { id: "fire-breath", resourceId: "fire-breath" }, placement: { targetIds: ["target"] } }
    : null,
  resolve: (sequence) => ({
    events: [{ event_type: "save", feature_id: "fire-breath" }],
    sequence: sequence + 1,
  }),
};
window.IRON_PIT_BROWSER_SAVES = {
  legalAction: () => false,
  resolveAction: () => { throw new Error("single save should not resolve"); },
};
window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION = {
  resolve: () => { throw new Error("standard attack should not resolve"); },
};
window.IRON_PIT_BROWSER_DODGE = { take: () => ({ event_type: "feature", feature_id: "dodge" }) };
window.IRON_PIT_BROWSER_STATE = { packTactics: () => false };
window.IRON_PIT_BROWSER_CHARGE = { openingFeature: () => null };

load("browser-main-action-profiles.js");
load("browser-main-action-selection.js");
load("browser-main-action-providers.js");
load("browser-signature-offense-providers.js");

const actor = {
  combatant_id: "dragon", side: "heroes",
  state: {
    action_available: true,
    template: {
      ruleset: "2024", intimidating_presence_2014_dc: 0,
      attack_action: { id: "multiattack", slots: [] },
      saving_throw_actions: [{
        id: "fire-breath", area: { shape: "cone" }, resourceId: "fire-breath",
      }],
      attacks: [],
    },
  },
};
const target = {
  combatant_id: "target", side: "monsters",
  state: { is_alive: true, is_dead: false, current_hp: 10, template: { ruleset: "2024" } },
};
const ctx = {
  sequence: 1, round: 1, turnKey: "1:dragon", member: actor,
  setup: { heroes: [actor], monsters: [target] },
};
const selector = window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION;
const candidates = selector.discoverCandidates("normalPostMove", ctx);
const selected = selector.selectCandidate("normalPostMove", candidates);

assert.equal(selected.providerId, "signature-area-save");
const resolved = selector.resolveCandidate("normalPostMove", selected, ctx);
assert.equal(resolved.events[0].feature_id, "fire-breath");

console.log("Browser signature save policy uses ready breath power before Multiattack.");
