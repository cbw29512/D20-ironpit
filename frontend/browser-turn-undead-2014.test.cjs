"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(`frontend/${name}`, "utf8"), { filename: name });

window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
load("browser-timed-conditions.js");
load("browser-action-economy.js");
load("browser-turn-creature-effects.js");

const source = { combatant_id: "cleric", state: { template: { name: "Cleric" } } };
const target = {
  combatant_id: "skeleton",
  state: {
    template: { name: "Skeleton" },
    active_effect_ids: [],
    timed_effects: [],
    action_available: true,
    bonus_action_available: true,
    reaction_available: true,
    is_dead: false,
    is_unconscious: false,
    turn_terminated: false,
  },
};

const applied = window.IRON_PIT_BROWSER_TURN_CREATURE_EFFECTS.apply(
  source, target, 1, "turn-undead", "turned-undead", {
    includeFrightened: false,
    includeIncapacitated: false,
    suppressReactions: true,
    endsIfSourceIncapacitated: false,
    endsIfSourceDead: false,
  },
);

assert.deepEqual(applied, ["turned-undead"]);
assert.equal(target.state.active_effect_ids.includes("frightened"), false);
assert.equal(target.state.active_effect_ids.includes("incapacitated"), false);
assert.equal(window.IRON_PIT_ACTION_ECONOMY.available(target.state, "reaction"), false);
assert.equal(window.IRON_PIT_ACTION_ECONOMY.available(target.state, "action"), true);
const effect = target.state.timed_effects.find((item) => item.effect_id === "turned-undead");
assert.equal(effect.turn_behavior, "forced_retreat");
assert.equal(effect.ends_on_damage, true);
assert.equal(effect.ends_if_source_incapacitated, false);
assert.equal(effect.ends_if_source_dead, false);

console.log("2014 Turn Undead lifecycle regressions passed.");
