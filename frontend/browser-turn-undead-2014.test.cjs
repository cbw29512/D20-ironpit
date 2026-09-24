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
window.IRON_PIT_BROWSER_POOLED_HEALING = {
  capacity: (member, numerator, denominator) => {
    const maximum = member.state.template.max_hp || member.state.current_hp;
    return Math.max(0, Math.floor(maximum * numerator / denominator) - member.state.current_hp);
  },
};
window.IRON_PIT_BROWSER_ZERO_HP = {
  reduceToZero: (state) => {
    state.current_hp = 0;
    state.is_alive = false;
    state.is_dead = true;
    state.is_unconscious = false;
    return "dead";
  },
};

load("browser-timed-conditions.js");
load("browser-action-economy.js");
load("browser-state.js");
load("browser-turn-creature-effects.js");
load("browser-source-bound-effects.js");
load("browser-condition-lifecycle.js");
load("browser-cleric-channel.js");

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

const cleric2014 = {
  combatant_id: "cleric-2014",
  side: "heroes",
  position_ft: 0,
  state: {
    template: { name: "Seraphine", archetype: "Cleric", ruleset: "2014", level: 2, traits: ["life-domain"] },
    current_hp: 19,
    is_alive: true,
    is_dead: false,
    action_available: true,
    resources: { "channel-divinity": 1, "spell-slot-1": 0 },
  },
};
const goblin2014 = {
  combatant_id: "goblin-2014",
  side: "monsters",
  position_ft: 10,
  state: {
    template: { name: "Goblin", creature_type: "humanoid", max_hp: 7, traits: [] },
    current_hp: 7, is_alive: true, is_dead: false,
  },
};
window.IRON_PIT_ACTION_ECONOMY = { available: () => true };
window.IRON_PIT_BROWSER_STATE = {
  ...window.IRON_PIT_BROWSER_STATE,
  distance: (a, b) => Math.abs(a.position_ft - b.position_ft),
  effectiveMaxHp: (state) => state.template.max_hp || state.current_hp,
};
assert.equal(
  window.IRON_PIT_BROWSER_CLERIC_CHANNEL.choose(
    cleric2014, { heroes: [cleric2014], monsters: [goblin2014] },
  ),
  null,
);

{
  window.IRON_PIT_BROWSER_SAVES = {
    resolveSavingThrow: () => ({ roll: { notation: "1d20", rolls: [1], modifier: 0, total: 1 }, succeeded: false }),
  };
  const destroySource = {
    combatant_id: "cleric-5",
    state: {
      template: {
        name: "Seraphine", turning_failure_destroy_max_cr: "1/2",
        ability_scores: { wisdom: 18 },
      },
    },
  };
  const low = {
    combatant_id: "skeleton-low",
    state: window.IRON_PIT_BROWSER_STATE.buildState({
      id: "skeleton-low", name: "Skeleton", kind: "monster", challenge_rating: "1/4",
      max_hp: 13, speed_ft: 30, size: "medium", resources: {},
    }),
  };
  const high = {
    combatant_id: "skeleton-high",
    state: window.IRON_PIT_BROWSER_STATE.buildState({
      id: "skeleton-high", name: "Greater Skeleton", kind: "monster", challenge_rating: "2",
      max_hp: 40, speed_ft: 30, size: "medium", resources: {},
    }),
  };
  const destroyed = window.IRON_PIT_BROWSER_TURN_CREATURE_EFFECTS.resolve(
    1, 1, destroySource, [low], 15, "turn-undead", "trembling", 0, "Turn Undead",
    { includeFrightened: false, includeIncapacitated: false },
  );
  assert.equal(low.state.is_dead, true);
  assert.equal(low.state.current_hp, 0);
  assert.deepEqual(destroyed.events[0].applied_condition_ids, []);

  const survived = window.IRON_PIT_BROWSER_TURN_CREATURE_EFFECTS.resolve(
    2, 1, destroySource, [high], 15, "turn-undead", "trembling", 0, "Turn Undead",
    { includeFrightened: false, includeIncapacitated: false, suppressAction: true },
  );
  assert.equal(high.state.is_dead, false);
  assert.ok(high.state.active_effect_ids.includes("trembling"));
  assert.deepEqual(survived.events[0].applied_condition_ids, ["trembling"]);
}

console.log("2014 Turn Undead trembling and Destroy Undead regressions passed.");
