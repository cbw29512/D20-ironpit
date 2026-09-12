"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

const member = {
  combatant_id: "attacker",
  side: "heroes",
  state: {
    action_available: true,
    is_dead: false,
    is_unconscious: false,
    turn_terminated: false,
    template: {
      attack_action: { id: "multi", slots: [{ saveActionIds: ["actor-owned-save"] }] },
      saving_throw_actions: [{ id: "actor-owned-save", resourceId: null, resourceCost: 1, range: 5 }],
      forced_movement_actions: [],
    },
  },
};
const target = { combatant_id: "target", state: {} };
const setup = { heroes: [member], monsters: [target] };

window.IRON_PIT_ACTION_ECONOMY = {
  available: (state) => state.action_available,
  spend: (state) => { state.action_available = false; },
};
window.IRON_PIT_BROWSER_FORMATION = {
  targetOrder: () => [target],
  saveDistance: () => 5,
  chooseAttack: () => null,
  isBackline: () => false,
  hasFrontlineTarget: () => false,
  hasBacklineTarget: () => false,
  flexibleSlotHasBoth: () => false,
  alliedFrontlineActive: () => false,
};
window.IRON_PIT_BROWSER_RESOURCES = { available: () => true };
window.IRON_PIT_BROWSER_FORCED_MOVEMENT_ACTION = { legalTargets: () => [] };
window.IRON_PIT_BROWSER_SAVES = {
  legalAction: (_action, _target, _distance, actor) => actor === member,
  resolveAction: (sequence) => ({ sequence, event_type: "saving_throw", feature_id: "actor-owned-save" }),
};
window.IRON_PIT_BROWSER_CHARGE = { openingFeature: () => null };
window.IRON_PIT_BROWSER_LIGHT_ATTACK = { resolve: (sequence) => ({ events: [], sequence }) };
window.IRON_PIT_BROWSER_ATTACK = {};
window.IRON_PIT_BROWSER_AURAS = { attackAdvantageSources: () => 0 };
window.IRON_PIT_BROWSER_STATE = { sizeAtMost: () => true, packTactics: () => false };
window.IRON_PIT_DICE = { roll: () => 1 };

load("browser-multiattack.js");

const result = window.IRON_PIT_BROWSER_MULTIATTACK.resolveAttackAction(1, 1, member, setup);

assert.equal(result.events.length, 1);
assert.equal(result.events[0].feature_id, "actor-owned-save");
assert.equal(member.state.action_available, false);

console.log("Browser Multiattack actor-owned save regression passed.");
