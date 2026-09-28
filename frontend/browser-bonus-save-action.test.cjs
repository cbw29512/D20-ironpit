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

load("browser-action-economy.js");
load("browser-ability-hooks.js");
load("browser-resources.js");
load("browser-resource-conversion.js");

window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_DEBUFF_COUNTERS = { movementCost: () => null };
load("browser-timed-conditions.js");

window.IRON_PIT_BROWSER_SAVING_THROWS = {
  resolveSavingThrow: (_state, _ability, dc) => ({
    roll: window.__saveRoll,
    succeeded: window.__saveRoll >= dc,
  }),
  saveMode: () => "normal",
};
window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage: (_state, amount) => amount,
  applyDamage: () => null,
};
window.IRON_PIT_BROWSER_GRAPPLE = { apply: () => [] };
window.IRON_PIT_BROWSER_STATE = { sizeAtMost: () => true };
window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS = {
  saveAdvantageSourceNames: () => [],
};
window.IRON_PIT_BROWSER_CONDITION_RULES = {
  canSee: () => true,
  autoFailStrDex: () => false,
};
window.IRON_PIT_DICE = { rollMany: () => [] };
load("browser-failed-save-timed-effects.js");
load("browser-saves.js");

window.IRON_PIT_BROWSER_AREA_TARGETING = {
  legalPlacements: (_member, _setup, _area, _range) => [{
    targetIds: ["monster:target"],
    friendlyIds: [],
    origin: [7.5, 2.5],
    direction: null,
  }],
};
load("browser-area-save-actions.js");
load("browser-bonus-save-actions.js");
load("browser-condition-lifecycle.js");

const action = {
  id: "intimidating-presence",
  name: "Intimidating Presence",
  actionCost: "bonus_action",
  saveAbility: "wisdom",
  dc: 18,
  range: 0,
  area: { shape: "emanation", origin: "self", radius_ft: 30 },
  resourceId: "intimidating-presence",
  resourceCost: 1,
  damageDiceCount: 0,
  effectTags: ["frightened"],
  failedSaveTimedEffect: {
    effectId: "frightened",
    durationRounds: 10,
    expiryTiming: "source_turn_start",
    repeatSaveAbility: "wisdom",
    repeatSaveDc: 18,
    repeatSaveTiming: "target_turn_end",
    nextAttackDisadvantage: false,
  },
};

const conversion = {
  id: "restore-intimidating-presence",
  name: "Intimidating Presence",
  actionCost: "none",
  sourceResourceId: "rage",
  sourceCost: 1,
  targetResourceId: "intimidating-presence",
  targetGain: 1,
  targetAllowsOverflow: false,
  priority: 50,
};

function state(name, resources) {
  return {
    template: {
      name,
      ruleset: "2024",
      creature_type: "humanoid",
      saving_throw_bonuses: { wisdom: 0 },
      saving_throw_actions: name === "Rokhan" ? [action] : [],
      resource_conversion_actions: name === "Rokhan" ? [conversion] : [],
      resources: name === "Rokhan"
        ? { rage: 5, "intimidating-presence": 1 }
        : {},
    },
    resources: { ...resources },
    active_effect_ids: [],
    active_modifiers: [],
    timed_effects: [],
    action_available: true,
    bonus_action_available: true,
    reaction_available: true,
    is_alive: true,
    is_dead: false,
    is_unconscious: false,
    current_hp: 20,
    temporary_hp: 0,
    death_save_successes: 0,
    death_save_failures: 0,
  };
}

function setupWith(resources) {
  const hero = {
    combatant_id: "hero:rokhan",
    side: "heroes",
    state: state("Rokhan", resources),
  };
  const target = {
    combatant_id: "monster:target",
    side: "monsters",
    state: state("Target", {}),
  };
  return { hero, target, setup: { heroes: [hero], monsters: [target] } };
}

window.__saveRoll = 1;
let { hero, target, setup } = setupWith({ rage: 2, "intimidating-presence": 1 });
let hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
let result = hooks.runPhase(hooks.PHASES.BONUS_ACTION_WINDOW, {
  sequence: 1,
  round: 1,
  member: hero,
  setup,
  turnKey: "1:hero:rokhan",
  bonusActionCheckpoint: "beforeEscape",
  events: [],
});

assert.equal(result.claimed, true);
assert.equal(result.events.length, 1);
assert.equal(result.events[0].feature_id, "intimidating-presence");
assert.deepEqual(result.events[0].applied_condition_ids, ["frightened"]);
assert.equal(hero.state.action_available, true);
assert.equal(hero.state.bonus_action_available, false);
assert.equal(hero.state.resources["intimidating-presence"], 0);
assert.deepEqual(target.state.active_effect_ids, ["frightened"]);
assert.equal(target.state.timed_effects[0].expires_round, 11);
assert.equal(target.state.timed_effects[0].repeat_save_ability, "wisdom");
assert.equal(target.state.timed_effects[0].repeat_save_dc, 18);
assert.equal(target.state.timed_effects[0].repeat_save_timing, "target_turn_end");
assert.equal(window.IRON_PIT_BROWSER_AREA_SAVES.choose(hero, setup), null);

window.__saveRoll = 20;
const repeat = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(
  10,
  1,
  target,
  "target_turn_end",
);
assert.equal(repeat.events[0].save_succeeded, true);
assert.deepEqual(repeat.events[0].removed_condition_ids, ["frightened"]);
assert.equal(target.state.active_effect_ids.includes("frightened"), false);

window.__saveRoll = 20;
({ hero, target, setup } = setupWith({ rage: 2, "intimidating-presence": 0 }));
result = hooks.runPhase(hooks.PHASES.BONUS_ACTION_WINDOW, {
  sequence: 1,
  round: 2,
  member: hero,
  setup,
  turnKey: "2:hero:rokhan",
  bonusActionCheckpoint: "beforeEscape",
  events: [],
});
assert.equal(result.claimed, true);
assert.equal(result.events[0].feature_id, "restore-intimidating-presence");
assert.equal(result.events[1].feature_id, "intimidating-presence");
assert.equal(hero.state.resources.rage, 1);
assert.equal(hero.state.resources["intimidating-presence"], 0);
assert.equal(hero.state.action_available, true);
assert.equal(hero.state.bonus_action_available, false);

console.log("Browser Bonus Action save / repeat-save / restoration parity passed.");
