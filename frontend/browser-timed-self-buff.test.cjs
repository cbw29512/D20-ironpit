"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
load("browser-action-economy.js");
load("browser-modifiers.js");
load("browser-timed-conditions.js");
load("browser-timed-self-buff.js");

const member = {
  combatant_id: "hero",
  state: {
    template: {
      name: "Hero",
      timed_self_buff: {
        source_id: "test-buff",
        resource_id: "ki",
        resource_cost: 4,
        duration_rounds: 10,
        effect_ids: ["invisible"],
        damage_resistances: ["fire", "cold"],
      },
    },
    action_available: true,
    bonus_action_available: true,
    reaction_available: true,
    turn_terminated: false,
    is_dead: false,
    is_unconscious: false,
    active_effect_ids: [],
    timed_effects: [],
    active_modifiers: [],
    resources: { ki: 10 },
  },
};

assert.equal(window.IRON_PIT_BROWSER_TIMED_SELF_BUFF.canActivate(member), true);
const event = window.IRON_PIT_BROWSER_TIMED_SELF_BUFF.resolve(1, 2, member);
assert.equal(event.feature_id, "test-buff");
assert.equal(member.state.resources.ki, 6);
assert.equal(member.state.action_available, false);
assert.ok(member.state.active_effect_ids.includes("invisible"));
assert.equal(member.state.timed_effects[0].expires_round, 12);
assert.equal(window.IRON_PIT_BROWSER_MODIFIERS.damageResistance(member.state, "fire"), true);
assert.equal(window.IRON_PIT_BROWSER_MODIFIERS.damageResistance(member.state, "force"), false);

const effect = member.state.timed_effects[0];
window.IRON_PIT_BROWSER_TIMED.removeGroup(member.state, effect);
window.IRON_PIT_BROWSER_MODIFIERS.removeSource([member.state], "hero", "test-buff");
assert.equal(member.state.active_effect_ids.includes("invisible"), false);
assert.equal(window.IRON_PIT_BROWSER_MODIFIERS.damageResistance(member.state, "fire"), false);

console.log("Universal timed self-buff applies and removes source-owned effects.");
