"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync("frontend/" + name, "utf8"), { filename: name },
);

window.IRON_PIT_DICE = {
  rolls: [],
  roll(sides) {
    if (!this.rolls.length) throw new Error("No queued d" + sides + " roll");
    return this.rolls.shift();
  },
};

load("browser-action-economy.js");
load("browser-resources.js");
load("browser-spellcasting.js");
load("browser-post-hit-damage.js");
load("browser-post-hit-save.js");

window.IRON_PIT_BROWSER_SAVES = {
  resolveSavingThrow(state, ability, dc) {
    const natural = window.IRON_PIT_DICE.roll(20);
    const total = natural + (state.template.saving_throw_bonuses?.[ability] || 0);
    return { roll: { total, rolls: [natural] }, succeeded: total >= dc };
  },
};
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = {
  immune: (state, conditionId) => (state.template.condition_immunities || []).includes(conditionId),
};

window.IRON_PIT_BROWSER_FORCED_MOVEMENT = {
  pushStraightAway(mover, _source, _setup, distanceFt) {
    mover.state.position = { x: mover.state.position.x + distanceFt / 5, y: mover.state.position.y };
    return distanceFt;
  },
};

const attack = { id: "longsword", name: "Longsword", diceCount: 1, diceSize: 8, damageBonus: 3, damageType: "slashing", onHitDamage: [] };

function hero(options) {
  return {
    template: {
      name: "Caster",
      level: 1,
      max_hp: 20,
      ability_scores: { strength: 16, dexterity: 10, constitution: 14, intelligence: 10, wisdom: 10, charisma: 14 },
      traits: [],
      unlimited_resources: [],
      condition_immunities: [],
      post_hit_damage_options: options,
    },
    current_hp: 20,
    resources: { "spell-slot-1": 1 },
    action_available: true,
    bonus_action_available: true,
    reaction_available: true,
    is_dead: false,
    is_unconscious: false,
    turn_terminated: false,
    spell_slot_expended_turn_key: null,
    feature_last_turn_keys: {},
    active_effect_ids: [],
    pending_post_hit_failed_save: null,
  };
}

const thunder = {
  source_id: "thunderous-smite-test",
  source_name: "Thunderous Smite",
  trigger_attack_ids: ["longsword"],
  action_cost: "bonus_action",
  printed_spell_level: 1,
  max_slot_level: 1,
  base_dice_count: 2,
  dice_per_slot_above: 0,
  dice_size: 6,
  damage_type: "thunder",
  bonus_target_creature_types: [],
  bonus_target_dice_count: 0,
  failed_save: { save_ability: "strength", dc_ability: "charisma", push_ft: 10, condition_id: "prone" },
};
const radiant = {
  ...thunder,
  source_id: "radiant-smite-test",
  source_name: "Radiant Smite",
  dice_size: 8,
  damage_type: "radiant",
  failed_save: null,
};

const target = {
  template: { name: "Target", max_hp: 40, creature_type: "humanoid", condition_immunities: [] },
  current_hp: 40,
  is_dead: false,
  is_alive: true,
};

window.IRON_PIT_DICE.rolls = [3, 3];
const caster = hero([thunder, radiant]);
const paid = window.IRON_PIT_BROWSER_POST_HIT_DAMAGE.bonusDamage(caster, attack, "1:hero", target);
assert.equal(paid.source, "Thunderous Smite");
assert.equal(caster.bonus_action_available, false);
assert.equal(caster.pending_post_hit_failed_save.condition_id, "prone");
assert.equal(window.IRON_PIT_BROWSER_POST_HIT_SAVE.spellSaveDc(caster, "charisma"), 12);

const member = { state: caster, combatant_id: "hero" };
const defender = {
  combatant_id: "target",
  state: {
    ...target,
    position: { x: 2, y: 1 },
    active_effect_ids: [],
    template: {
      ...target.template,
      saving_throw_bonuses: { strength: 0 },
    },
  },
};
window.IRON_PIT_DICE.rolls = [1];
const failed = window.IRON_PIT_BROWSER_POST_HIT_SAVE.resolve(member, defender, { map_definition: {} });
assert.equal(failed.saveSucceeded, false);
assert.equal(failed.pushedFt, 10);
assert.deepEqual(defender.state.active_effect_ids, ["prone"]);
assert.equal(defender.state.position.x, 4);
assert.equal(caster.pending_post_hit_failed_save, null);

console.log("Browser post-hit failed-save regressions passed.");
