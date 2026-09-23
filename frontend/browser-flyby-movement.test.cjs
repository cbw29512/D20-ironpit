"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
window.IRON_PIT_BROWSER_GRAPPLE = { speedIsZero: () => false };
window.IRON_PIT_BROWSER_MODIFIERS = { effectiveSpeed: (state) => state.template.speed_ft };
window.IRON_PIT_BROWSER_CONDITION_RULES = {
  has: () => false,
  incapacitated: () => false,
};
window.IRON_PIT_BROWSER_EXHAUSTION = null;
window.IRON_PIT_BROWSER_GRID_GEOMETRY = null;
window.IRON_PIT_BROWSER_OPENING_MODIFIERS = { build: () => [] };
window.IRON_PIT_BROWSER_HEROIC_INSPIRATION = { grant: () => {} };
window.IRON_PIT_ACTION_ECONOMY = { available: () => true, spend: () => {} };
window.IRON_PIT_BROWSER_ATTACK = { resolveAttack: () => ({ event_type: "attack" }) };

vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-state.js"), "utf8"), {
  filename: "browser-state.js",
});
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-reactions.js"), "utf8"), {
  filename: "browser-reactions.js",
});

const S = window.IRON_PIT_BROWSER_STATE;
const R = window.IRON_PIT_BROWSER_REACTIONS;

const flyerTemplate = {
  id: "2014-giant-owl",
  name: "Giant Owl",
  max_hp: 19,
  speed_ft: 60,
  movement_modes: { walk_ft: 5, fly_ft: 60, climb_ft: 0, swim_ft: 0, burrow_ft: 0, hover: false },
  opportunity_attack_exempt_movement_modes: ["fly"],
  resources: {},
  attacks: [],
};

const flyerState = S.buildState(flyerTemplate);
assert.equal(flyerState.movement_mode, "fly");
S.beginTurn(flyerState);
assert.equal(flyerState.movement_mode, "fly");
assert.equal(flyerState.movement_remaining_ft, 60);

const reactor = {
  combatant_id: "fighter",
  side: "heroes",
  state: {
    active_modifiers: [],
    reaction_available: true,
    template: {
      name: "Fighter",
      attacks: [{ id: "sword", kind: "melee", reach: 5 }],
    },
  },
};
const mover = { combatant_id: "owl", side: "monsters", state: flyerState };

assert.equal(R.opportunityAttackWeapon(reactor, mover, 5, 10, "speed"), null);
mover.state.movement_mode = "walk";
assert.equal(R.opportunityAttackWeapon(reactor, mover, 5, 10, "speed").id, "sword");
