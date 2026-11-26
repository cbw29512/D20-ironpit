"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
for (const file of [
  "browser-action-economy.js", "browser-modifier-validation.js", "browser-modifiers.js",
  "browser-timed-conditions.js", "browser-concentration.js", "browser-spell-modifiers.js",
  "browser-state.js", "browser-environment-contexts.js", "browser-environment-context-actions.js",
  "browser-timed-self-buff-policy.js", "browser-timed-self-buffs.js",
  "browser-effective-senses.js", "browser-condition-rules.js", "browser-rolls.js",
  "browser-attack-outcome.js", "browser-illusory-duplicates.js", "browser-attack.js",
]) load(file);

function queuedDice(values) {
  const queue = [...values];
  const roll = (sides) => {
    const value = queue.shift();
    if (!Number.isInteger(value) || value < 1 || value > sides) throw new Error(`invalid d${sides}: ${value}`);
    return value;
  };
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
}

const phantasms = {
  id: "phantasms", name: "Phantasms", actionCost: "action", activationTiming: "action",
  resourceId: "phantasms", resourceCost: 1, conditionIds: [], magicalEffect: true,
  prohibitedEnvironmentContextId: "bright_light",
  expiryTiming: null, animation: "mirror-image",
  illusoryDuplicateDefense: {
    initialDuplicates: 3, redirectionMode: "uniform_original_and_duplicates",
    redirectMinimumByDuplicates: [0, 11, 8, 6], armorClassMode: "source_armor_class",
    armorClassBase: 10, armorClassAbility: "dexterity",
    bypassAttackerSenses: ["blindsight", "truesight"],
  },
};
const attack = { id: "club", weaponId: "club", name: "Club", kind: "melee", bonus: 2,
  damageBonus: 0, damageType: "bludgeoning", diceCount: 1, diceSize: 4,
  reach: 5, projectile: null, attackAbility: "strength" };
function state(id, defender = false) {
  return { template: { id, name: id, armor_class: defender ? 14 : 10, max_hp: 20, speed_ft: 30,
    ability_scores: { strength: 10, dexterity: 10, constitution: 10, intelligence: 10, wisdom: 10, charisma: 10 },
    timed_self_buff_actions: defender ? [phantasms] : [], innate_condition_ids: [], condition_immunities: [],
    blindsight_ft: 0, truesight_ft: 0, resource_backed_d20_bonus_dice: [], failed_d20_test_override_grants: [] },
    resources: defender ? { phantasms: { current_uses: 1, max_uses: 1 } } : {}, current_hp: 20,
    temporary_hp: 0, is_alive: true, is_dead: false, is_unconscious: false, is_stable: false,
    action_available: true, bonus_action_available: true, reaction_available: true, movement_remaining_ft: 30,
    active_effect_ids: [], active_modifiers: [], timed_effects: [], concentration: null,
    voluntary_turn_activity: null, delayed_resource_refills: [], feature_use_counts: {}, feature_last_turn_keys: {},
    ability_score_reductions: {}, turns_started: 0, death_save_successes: 0, death_save_failures: 0 };
}
const attacker = { combatant_id: "hero", side: "heroes", position_ft: 5, state: state("hero") };
const defender = { combatant_id: "cloaker", side: "monsters", position_ft: 0, state: state("cloaker", true) };
window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS.resolve(1, 1, defender, phantasms, { affectedStates: [defender.state] });
window.IRON_PIT_DICE = queuedDice([2, 12]);
const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(2, 1, attacker, defender, attack, 5);
assert.equal(event.feature_id, "phantasms");
assert.equal(event.feature_roll.notation, "1d4");
assert.equal(event.target_ac, 14);
assert.equal(event.hp_before, event.hp_after);
assert.equal(defender.state.timed_effects[0].illusory_duplicates_remaining, 2);

defender.state.action_available = true;
defender.state.resources.phantasms = 1;
defender.state.timed_effects = [];
defender.state.active_effect_ids = [];
const lightAction = {
  id: "illumination", name: "Illumination", action_cost: "bonus_action",
  initial_mode_id: "dark", ai_mode_id: "bright",
  modes: [
    { id: "dark", emitted_contexts: [] },
    { id: "bright", emitted_contexts: [{ context_id: "bright_light", radius_ft: 30 }] },
  ],
};
const light = { combatant_id: "light", side: "heroes", position_ft: 0, state: state("light") };
light.state.template.environment_context_control_actions = [lightAction];
light.state.environment_context_modes = { illumination: "dark" };
const setup = { heroes: [light], monsters: [defender] };
window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS.resolve(3, 1, defender, phantasms, {
  setup, affectedStates: [light.state, defender.state],
});
assert.equal(defender.state.timed_effects[0].illusory_duplicates_remaining, 3);
const bright = lightAction.modes[1];
const lightEvent = window.IRON_PIT_BROWSER_ENVIRONMENT_CONTEXT_ACTIONS.resolve(
  4, 1, light, lightAction, bright, [light.state, defender.state], setup,
);
assert.equal(defender.state.timed_effects.length, 0);
assert.match(lightEvent.description, /cloaker's Phantasms ends/i);
defender.state.action_available = true;
defender.state.resources.phantasms = 1;
assert.throws(() => window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS.resolve(5, 1, defender, phantasms, {
  setup, affectedStates: [light.state, defender.state],
}), /cannot be activated in bright light/);

console.log("2014 Phantasms browser interception and bright-light lifecycle passed.");
