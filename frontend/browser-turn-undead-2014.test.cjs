"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(`frontend/${name}`, "utf8"), { filename: name });

window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_GRAPPLE = { speedIsZero: () => false };
window.IRON_PIT_BROWSER_MODIFIERS = { effectiveSpeed: (state) => state.template.speed_ft, expireTargetTurn: () => {} };
window.IRON_PIT_BROWSER_CONDITION_RULES = { incapacitated: () => false };
window.IRON_PIT_BROWSER_OPENING_MODIFIERS = { build: () => [] };
window.IRON_PIT_BROWSER_EXHAUSTION = {};
window.IRON_PIT_BROWSER_HEROIC_INSPIRATION = { grant: () => {} };

load("browser-timed-conditions.js");
load("browser-action-economy.js");
load("browser-state.js");
load("browser-turn-creature-effects.js");
load("browser-source-bound-effects.js");
load("browser-condition-lifecycle.js");

const source = { combatant_id: "cleric", state: { template: { name: "Cleric" } } };
const target = {
  combatant_id: "skeleton",
  state: window.IRON_PIT_BROWSER_STATE.buildState({
    id: "skeleton", name: "Skeleton", max_hp: 13, speed_ft: 30, size: "medium", resources: {},
  }),
};

function applyTrembling() {
  const applied = window.IRON_PIT_BROWSER_TURN_CREATURE_EFFECTS.apply(
    source, target, 1, "turn-undead", "trembling", {
      includeFrightened: false,
      includeIncapacitated: false,
      suppressAction: true,
      suppressBonusAction: true,
      suppressReactions: true,
      suppressMovement: true,
      turnBehavior: "normal",
      repeatSaveTiming: "target_turn_end",
      saveDc: 13,
      expiresRounds: null,
      expiryTiming: null,
      endsIfSourceIncapacitated: false,
      endsIfSourceDead: false,
    },
  );
  assert.deepEqual(applied, ["trembling"]);
}

applyTrembling();
assert.equal(target.state.active_effect_ids.includes("frightened"), false);
assert.equal(target.state.active_effect_ids.includes("incapacitated"), false);
window.IRON_PIT_BROWSER_STATE.beginTurn(target.state);
assert.equal(window.IRON_PIT_ACTION_ECONOMY.available(target.state, "action"), false);
assert.equal(window.IRON_PIT_ACTION_ECONOMY.available(target.state, "bonus_action"), false);
assert.equal(window.IRON_PIT_ACTION_ECONOMY.available(target.state, "reaction"), false);
assert.equal(target.state.movement_remaining_ft, 0);

let effect = target.state.timed_effects.find((item) => item.effect_id === "trembling");
assert.equal(effect.turn_behavior, "normal");
assert.equal(effect.repeat_save_ability, "wisdom");
assert.equal(effect.repeat_save_dc, 13);
assert.equal(effect.repeat_save_timing, "target_turn_end");
assert.equal(effect.expires_round, null);
assert.equal(effect.ends_on_damage, true);

window.IRON_PIT_BROWSER_SAVES = {
  resolveSavingThrow: () => ({ roll: { notation: "1d20", rolls: [20], modifier: 0, total: 20 }, succeeded: true }),
};
let result = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(
  1, 1, target, "target_turn_end",
);
assert.equal(result.events[0].save_succeeded, true);
assert.deepEqual(result.events[0].removed_condition_ids, ["trembling"]);
assert.equal(target.state.active_effect_ids.includes("trembling"), false);

applyTrembling();
const removed = window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS.endDamageSensitive(target.state);
assert.deepEqual(removed, ["trembling"]);
assert.equal(target.state.active_effect_ids.includes("trembling"), false);

console.log("2014 Turn Undead trembling regressions passed.");
