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
  chooseStandardAttack: () => null,
  saveDistance: () => 5,
};
window.IRON_PIT_BROWSER_SPELL_OFFENSE = {
  choose: () => null,
  resolveChoice: (sequence) => ({ events: [], sequence }),
};
window.IRON_PIT_BROWSER_MULTIATTACK = {
  available: () => false,
  resolveAttackAction: (sequence) => ({ events: [], sequence }),
};
window.IRON_PIT_BROWSER_AREA_SAVES = {
  choose: () => null,
  resolve: (sequence) => ({ events: [], sequence }),
};
window.IRON_PIT_BROWSER_SAVES = {
  legalAction: () => false,
  resolveAction: () => { throw new Error("save action must not resolve"); },
};
window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION = {
  resolve: () => { throw new Error("standard attack must not resolve"); },
};
window.IRON_PIT_BROWSER_DODGE = {
  take: () => { throw new Error("Dodge must not resolve"); },
};
window.IRON_PIT_BROWSER_STATE = { packTactics: () => false };
window.IRON_PIT_BROWSER_CHARGE = { openingFeature: () => null };

load("browser-main-action-profiles.js");
load("browser-main-action-selection.js");
load("browser-main-action-providers.js");

const selector = window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION;
const actor = {
  combatant_id: "hero-2014",
  side: "heroes",
  state: {
    action_available: false,
    template: {
      ruleset: "2014",
      intimidating_presence_2014_dc: 0,
      attacks: [],
      saving_throw_actions: [],
    },
  },
};
const target = {
  combatant_id: "monster-1",
  side: "monsters",
  state: { template: { ruleset: "2014" }, is_alive: true, is_dead: false },
};
const ctx = {
  sequence: 1,
  round: 1,
  turnKey: "1:hero-2014",
  member: actor,
  setup: { heroes: [actor], monsters: [target] },
};

delete window.IRON_PIT_BROWSER_INTIMIDATING_PRESENCE_2014;
assert.deepEqual(
  selector.discoverCandidates("normalPostMove", ctx),
  [],
  "actors without Intimidating Presence must not require its runtime",
);

actor.state.template.intimidating_presence_2014_dc = 15;
assert.throws(
  () => selector.discoverCandidates("normalPostMove", ctx),
  /Intimidating Presence runtime is not loaded/,
  "feature owners must fail closed when the runtime is missing",
);

console.log("Browser Main Action provider dependency gating passed.");
