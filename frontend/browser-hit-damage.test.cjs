"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
let diceQueue = [];
const queueDice = (values) => {
  diceQueue = [...values];
  window.IRON_PIT_DICE = {
    roll: (sides) => { const value = diceQueue.shift(); assert.ok(value >= 1 && value <= sides); return value; },
    rollMany: (count, sides) => Array.from({ length: count }, () => window.IRON_PIT_DICE.roll(sides)),
  };
};

let saveSucceeded = false;
window.IRON_PIT_BROWSER_SAVES = {
  resolveSavingThrow: (_state, ability, dc) => ({
    roll: { notation: "1d20", rolls: [saveSucceeded ? dc : dc - 1], modifier: 0,
      selected_roll: saveSucceeded ? dc : dc - 1, mode: "normal", total: saveSucceeded ? dc : dc - 1 },
    succeeded: saveSucceeded,
  }),
  resolveOnHitConditionSave: () => null,
};
window.IRON_PIT_BROWSER_ROLLS = {
  weaponDamage: (attacker, attack, critical, _mode, turnKey, _bonusDamage = null, target = null,
    _sneakAllyAvailable = false, activeAllyAdjacentToTarget = false) => {
    const rolls = critical ? [4, 4] : [4];
    const component = { source: attack.name, damage_type: attack.damageType,
      notation: `${rolls.length}d4+0`, rolls, modifier: 0, total: rolls.reduce((a, b) => a + b, 0) };
    const components = [component];
    for (const spec of window.IRON_PIT_BROWSER_ONCE_PER_TURN_HIT_DAMAGE?.bonusDamages(
      attacker, turnKey, target, attack, activeAllyAdjacentToTarget,
    ) || []) {
      const count = spec.diceCount * (critical ? 2 : 1);
      const riderRolls = window.IRON_PIT_DICE.rollMany(count, spec.diceSize);
      components.push({
        source: spec.source, damage_type: spec.damageType, notation: `${count}d${spec.diceSize}+0`,
        rolls: riderRolls, modifier: 0, total: riderRolls.reduce((a, b) => a + b, 0),
      });
    }
    return {
      roll: {
        notation: components.map((item) => item.notation).join(" + "),
        rolls: components.flatMap((item) => item.rolls),
        modifier: 0,
        total: components.reduce((sum, item) => sum + item.total, 0),
      },
      components,
    };
  },
  attackMode: () => "normal",
  d20: (modifier) => ({ notation: "1d20", rolls: [15], modifier, selected_roll: 15, mode: "normal", total: 15 + modifier }),
};
window.IRON_PIT_BROWSER_ZERO_HP = {
  applyDamage: (state, amount) => {
    state.current_hp = Math.max(0, state.current_hp - amount);
    state.is_dead = state.current_hp === 0; state.is_alive = !state.is_dead;
    return state.is_dead ? "dead" : "damaged";
  },
  stabilizeAtZero: (state) => {
    state.current_hp = 0; state.is_dead = false; state.is_alive = true;
    state.is_unconscious = true; state.is_stable = true;
    state.death_save_successes = 0; state.death_save_failures = 0;
    return "unconscious";
  },
};
window.IRON_PIT_BROWSER_TIMED = {
  nextAttackDisadvantage: () => 0, consumeNextAttackDisadvantage: () => 0,
  apply: (state, effectId, sourceId, options) => {
    state.timed_effects.push({ effect_id: effectId, source_id: sourceId, ...options });
    if (!state.active_effect_ids.includes(effectId)) state.active_effect_ids.push(effectId);
    return effectId;
  },
};
window.IRON_PIT_ACTION_ECONOMY = { available: () => true, spend: () => {} };

load("browser-state.js");
load("browser-once-per-turn-hit-damage.js");
load("browser-ability-hooks.js");
load("browser-attack-outcome.js");
load("browser-damage-defense-rules.js");
load("browser-attack.js");
load("browser-damage-defense-rules.js");
load("browser-hit-damage.js");

const attack = {
  id: "sting", name: "Sting", kind: "melee", bonus: 5, reach: 5,
  diceCount: 1, diceSize: 4, damageBonus: 0, damageType: "piercing",
  onHitSaveDamage: { source: "Sting poison", saveAbility: "constitution", dc: 11,
    diceCount: 3, diceSize: 6, damageBonus: 0, damageType: "poison", successDamage: "half" },
};
const riderAttack = {
  ...attack,
  onHitSaveDamage: {
    ...attack.onHitSaveDamage,
    zeroHpRider: { stable: true, conditionIds: ["poisoned", "paralyzed"], durationRounds: 600 },
  },
};
const state = (resist = [], immune = []) => ({
  template: { name: "Target", ruleset: "2014", armor_class: 10, max_hp: 40, saving_throw_bonuses: { constitution: 0 },
    damage_resistances: resist, damage_vulnerabilities: [], damage_immunities: immune, traits: [] },
  current_hp: 40, temporary_hp: 0, temporary_damage_resistances: [], active_effect_ids: [], timed_effects: [],
  death_save_successes: 0, death_save_failures: 0, is_stable: false, is_dead: false, is_alive: true,
  is_unconscious: false,
});
const attackerState = { template: { name: "Wyvern", ruleset: "2014", max_hp: 110, armor_class: 13, traits: [] }, current_hp: 110,
  active_effect_ids: [], feature_last_turn_keys: {}, action_available: true };

saveSucceeded = false; queueDice([6, 5, 4]);
let target = state();
let result = window.IRON_PIT_BROWSER_HIT_DAMAGE.resolve(attackerState, target, attack, true, "normal", "1:wyvern");
assert.equal(result.damageComponents[0].total, 8, "critical doubles the weapon dice");
assert.deepEqual(result.damageComponents[1].rolls, [6, 5, 4], "save damage dice are never critical-doubled");
assert.equal(result.damageComponents[1].total, 15);
assert.equal(result.damageRoll.total, 23);
assert.equal(target.current_hp, 17, "weapon and poison apply as one hit total");
assert.equal(result.saveDamage.saveDc, 11);
assert.equal(result.saveDamage.saveSucceeded, false);

saveSucceeded = true; queueDice([6, 5, 4]);
target = state();
result = window.IRON_PIT_BROWSER_HIT_DAMAGE.resolve(attackerState, target, attack, false, "normal", "2:wyvern");
assert.equal(result.damageComponents[1].total, 7, "successful half damage floors once before defenses");
assert.equal(result.damageRoll.total, 11);

saveSucceeded = true; queueDice([]);
target = state();
result = window.IRON_PIT_BROWSER_HIT_DAMAGE.resolve(attackerState, target,
  { ...attack, onHitSaveDamage: { ...attack.onHitSaveDamage, successDamage: "none" } }, false, "normal", "3:snake");
assert.equal(result.damageComponents.length, 1, "successful no-damage save does not roll poison dice");
assert.equal(diceQueue.length, 0);

saveSucceeded = false; queueDice([6, 5, 4]);
target = state(["poison"]);
result = window.IRON_PIT_BROWSER_HIT_DAMAGE.resolve(attackerState, target, attack, false, "normal", "4:scorpion");
assert.equal(result.damageComponents[1].applied_total, 7, "poison resistance applies to the save damage component");

saveSucceeded = false; queueDice([6, 5, 4]);
target = state([], ["poison"]);
result = window.IRON_PIT_BROWSER_HIT_DAMAGE.resolve(attackerState, target, attack, false, "normal", "5:scorpion");
assert.equal(result.damageComponents[1].applied_total, 0, "poison immunity applies to the save damage component");

saveSucceeded = false; queueDice([6, 5, 4]);
target = state(); target.current_hp = 10;
result = window.IRON_PIT_BROWSER_HIT_DAMAGE.resolve(attackerState, target, riderAttack, false, "normal", "1:giant-wasp");
assert.equal(result.damageOutcome, "unconscious");
assert.equal(target.current_hp, 0); assert.equal(target.is_stable, true); assert.equal(target.is_dead, false);
assert.deepEqual(target.active_effect_ids.sort(), ["paralyzed", "poisoned"]);
assert.equal(target.timed_effects.length, 2);
for (const effect of target.timed_effects) {
  assert.equal(effect.source_id, "giant-wasp");
  assert.equal(effect.sourceEffectId, "Sting poison:zero-hp-save-damage");
  assert.equal(effect.appliedRound, 1); assert.equal(effect.expiresRound, 601);
  assert.equal(effect.expiryTiming, "target_turn_start");
  assert.equal(effect.useDefaultPoisonRecovery, false);
}

saveSucceeded = false; queueDice([6, 5, 4]);
target = state(); target.current_hp = 4;
result = window.IRON_PIT_BROWSER_HIT_DAMAGE.resolve(attackerState, target, riderAttack, false, "normal", "2:giant-wasp");
assert.equal(target.is_dead, true, "rider must not fire when weapon damage alone caused 0 HP");
assert.equal(target.timed_effects.length, 0);

saveSucceeded = false; queueDice([6, 5, 4]);
const defender = { combatant_id: "target", side: "monsters", state: state() };
const actor = { combatant_id: "wyvern", side: "heroes", state: attackerState };
const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(1, 1, actor, defender, attack, 5, { spendAction: false });
assert.equal(event.save_ability, "constitution");
assert.equal(event.save_dc, 11);
assert.equal(event.save_succeeded, false);
assert.equal(event.saving_throw_roll.total, 10);
assert.equal(event.damage_components.length, 2);
assert.equal(event.hp_before - event.hp_after, event.damage_roll.total, "attack event records one combined HP change");

const irresistibleAttack = { ...attack, id: "greataxe", name: "Greataxe", damageType: "slashing", onHitSaveDamage: null };
const irresistibleAttacker = {
  ...attackerState,
  template: {
    ...attackerState.template,
    ability_scores: { strength: 21, dexterity: 13, constitution: 20, intelligence: 10, wisdom: 10, charisma: 10 },
    damage_resistance_bypass_grants: [{
      source_id: "boon-irresistible-offense", source_name: "Boon of Irresistible Offense",
      damage_types: ["bludgeoning", "piercing", "slashing"],
    }],
    natural_twenty_attack_damage_grants: [{
      source_id: "boon-irresistible-offense", source_name: "Boon of Irresistible Offense",
      ability: "strength", damage_type_source: "attack",
    }],
  },
};
target = state(["slashing"]);
result = window.IRON_PIT_BROWSER_HIT_DAMAGE.resolve(
  irresistibleAttacker, target, irresistibleAttack, true, "normal", "19:rokhan", { naturalRoll: 20 },
);
assert.equal(result.damageComponents.length, 2);
assert.equal(result.damageComponents[0].applied_total, 8, "Irresistible Offense bypasses slashing Resistance");
assert.equal(result.damageComponents[1].source, "Boon of Irresistible Offense");
assert.equal(result.damageComponents[1].total, 21);
assert.equal(result.damageComponents[1].applied_total, 21);
assert.equal(result.damageComponents[1].damage_type, "slashing");

target = state(["slashing"]);
result = window.IRON_PIT_BROWSER_HIT_DAMAGE.resolve(
  irresistibleAttacker, target, irresistibleAttack, true, "normal", "19:rokhan-other-crit", { naturalRoll: 19 },
);
assert.equal(result.damageComponents.length, 1, "expanded critical ranges must not trigger natural-20 damage");
assert.equal(result.damageComponents[0].applied_total, 8, "Resistance bypass still applies without the natural-20 rider");

target = state(["slashing"]);
result = window.IRON_PIT_BROWSER_HIT_DAMAGE.resolve(
  attackerState, target, irresistibleAttack, true, "normal", "18:rokhan", { naturalRoll: 20 },
);
assert.equal(result.damageComponents.length, 1);
assert.equal(result.damageComponents[0].applied_total, 4, "combatants without a bypass grant still respect Resistance");

const martialAttackerState = {
  ...attackerState,
  template: {
    ...attackerState.template,
    once_per_turn_weapon_hit_damage_rider: {
      source_id: "martial-advantage", source_name: "Martial Advantage",
      dice_count: 2, dice_size: 6, flat_bonus: 0, damage_type: null,
      requires_active_ally_adjacent_to_target: true,
    },
  },
  feature_last_turn_keys: {},
};
const martialActor = { combatant_id: "hobgoblin", side: "heroes", position_ft: 0, state: martialAttackerState };
const martialAlly = { combatant_id: "ally", side: "heroes", position_ft: 10, state: state() };
const martialTarget = { combatant_id: "martial-target", side: "monsters", position_ft: 5, state: state() };
const martialSetup = { heroes: [martialActor, martialAlly], monsters: [martialTarget] };

queueDice([5, 6]);
result = window.IRON_PIT_BROWSER_HIT_DAMAGE.resolve(
  martialAttackerState, martialTarget.state, irresistibleAttack, false, "normal", "1:hobgoblin",
  { setup: martialSetup },
);
assert.equal(result.damageComponents.find((item) => item.source === "Martial Advantage").total, 11);

queueDice([]);
result = window.IRON_PIT_BROWSER_HIT_DAMAGE.resolve(
  martialAttackerState, martialTarget.state, irresistibleAttack, false, "normal", "1:hobgoblin",
  { setup: martialSetup },
);
assert.equal(result.damageComponents.some((item) => item.source === "Martial Advantage"), false,
  "Martial Advantage fires only once on the active turn");

martialAlly.position_ft = 20;
queueDice([]);
result = window.IRON_PIT_BROWSER_HIT_DAMAGE.resolve(
  martialAttackerState, martialTarget.state, irresistibleAttack, false, "normal", "2:hobgoblin",
  { setup: martialSetup },
);
assert.equal(result.damageComponents.some((item) => item.source === "Martial Advantage"), false,
  "Martial Advantage requires the shared target-adjacent active-ally predicate");

load("browser-monsters-2014.js");
const roster = window.IRON_PIT_BROWSER_MONSTERS_2014;
assert.equal(Object.keys(roster).length, 205);
for (const id of [
  "giant-centipede", "giant-poisonous-snake", "giant-scorpion", "giant-wasp", "poisonous-snake", "scorpion", "wyvern",
]) {
  const monster = roster[`2014-${id}`];
  assert.ok(monster, `${id} must be in the certified 2014 browser roster`);
  assert.ok(monster.attacks.some((item) => item.onHitSaveDamage), `${id} must carry save damage into the browser`);
}
for (const id of ["giant-centipede", "giant-wasp"]) {
  const rider = roster[`2014-${id}`].attacks.find((item) => item.onHitSaveDamage?.zeroHpRider)?.onHitSaveDamage.zeroHpRider;
  assert.ok(rider, `${id} must carry the zero-HP save rider through generated browser serialization`);
  assert.equal(rider.stable, true);
  assert.deepEqual(rider.conditionIds.sort(), ["paralyzed", "poisoned"]);
  assert.equal(rider.durationRounds, 600);
}

console.log("Browser hit damage, including Martial Advantage adjacency, remains certified across the 201-monster 2014 roster.");