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
  "browser-timed-self-buff-policy.js", "browser-timed-self-buffs.js",
  "browser-effective-senses.js", "browser-condition-rules.js",
  "browser-rolls.js", "browser-attack-outcome.js", "browser-illusory-duplicates.js",
  "browser-attack.js",
]) load(file);

function queuedDice(values, fallback = 10) {
  const queue = [...values];
  const roll = (sides) => ((queue.length ? queue.shift() : fallback) - 1) % sides + 1;
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
}

const mirror = {
  id: "mirror-image", name: "Mirror Image", actionCost: "action", activationTiming: "action",
  resourceId: null, resourceCost: 1, durationRounds: 10, conditionIds: [], magicalEffect: true,
  expiryTiming: "source_turn_start", animation: "mirror-image",
  illusoryDuplicateDefense: {
    initialDuplicates: 3, redirectMinimumByDuplicates: [0, 11, 8, 6],
    armorClassBase: 10, armorClassAbility: "dexterity",
    bypassAttackerSenses: ["blindsight", "truesight"],
  },
};
const attack = {
  id: "club", weaponId: "club", name: "Club", kind: "melee", bonus: 2,
  damageBonus: 0, damageType: "bludgeoning", diceCount: 1, diceSize: 4,
  reach: 5, projectile: null, attackAbility: "strength",
};
function state(id, dexterity = 10) {
  return {
    template: {
      id, name: id, armor_class: 10, max_hp: 20, speed_ft: 30,
      ability_scores: { strength: 10, dexterity, constitution: 10, intelligence: 10, wisdom: 10, charisma: 10 },
      timed_self_buff_actions: id === "defender" ? [mirror] : [],
      innate_condition_ids: [], condition_immunities: [], blindsight_ft: 0, truesight_ft: 0,
      resource_backed_d20_bonus_dice: [], failed_d20_test_override_grants: [],
    },
    resources: {}, current_hp: 20, temporary_hp: 0, is_alive: true, is_dead: false,
    is_unconscious: false, is_stable: false, action_available: true,
    bonus_action_available: true, reaction_available: true, movement_remaining_ft: 30,
    active_effect_ids: [], active_modifiers: [], timed_effects: [], concentration: null,
    voluntary_turn_activity: null, delayed_resource_refills: [], feature_use_counts: {},
    feature_last_turn_keys: {}, ability_score_reductions: {}, turns_started: 0,
    death_save_successes: 0, death_save_failures: 0,
  };
}

const attacker = { combatant_id: "attacker", side: "heroes", position_ft: 5, state: state("attacker") };
const defender = { combatant_id: "defender", side: "monsters", position_ft: 0, state: state("defender", 14) };
window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS.resolve(1, 1, defender, mirror, { affectedStates: [defender.state] });
assert.equal(defender.state.timed_effects[0].illusory_duplicates_remaining, 3);

attacker.state.action_available = true;
window.IRON_PIT_DICE = queuedDice([6, 10]);
const hit = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(2, 1, attacker, defender, attack, 5);
assert.equal(hit.feature_id, "mirror-image");
assert.equal(hit.feature_roll.total, 6);
assert.equal(hit.target_ac, 12);
assert.equal(hit.hit, true);
assert.equal(hit.hp_before, hit.hp_after);
assert.equal(defender.state.timed_effects[0].illusory_duplicates_remaining, 2);

attacker.state.action_available = true;
window.IRON_PIT_DICE = queuedDice([8, 1]);
const miss = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(3, 1, attacker, defender, attack, 5);
assert.equal(miss.feature_id, "mirror-image");
assert.equal(miss.hit, false);
assert.equal(defender.state.timed_effects[0].illusory_duplicates_remaining, 2);

attacker.state.template.blindsight_ft = 10;
window.IRON_PIT_DICE = queuedDice([20]);
assert.equal(
  window.IRON_PIT_BROWSER_ILLUSORY_DUPLICATES.intercept(attacker.state, defender.state, 5),
  null,
);

const fresh = state("defender", 14);
assert.deepEqual(fresh.timed_effects, []);
assert.equal(fresh.template.ability_scores.dexterity, 14);

console.log("2014 Mirror Image browser activation, attack interception, senses, and reset passed.");
