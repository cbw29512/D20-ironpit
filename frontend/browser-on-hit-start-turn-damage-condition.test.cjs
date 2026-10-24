"use strict";
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

const S = window.IRON_PIT_BROWSER_STATE;
const A = window.IRON_PIT_BROWSER_ATTACK;
const Burn = window.IRON_PIT_BROWSER_START_OF_TURN_TIMED_BURN;
const Lifecycle = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE;
const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];

function setDice(values) {
  try {
    const queue = [...values];
    window.IRON_PIT_DICE = {
      roll(sides) {
        const value = queue.shift();
        if (!(value >= 1 && value <= sides)) throw new Error("invalid d" + sides + ": " + value);
        return value;
      },
      rollMany(count, sides) {
        return Array.from({ length: count }, () => this.roll(sides));
      },
    };
  } catch (error) {
    console.error("Failed to configure start-turn condition dice", { error });
    throw error;
  }
}

function member(id, side, position) {
  try {
    const template = structuredClone(base);
    Object.assign(template, {
      id: "template-" + id, name: id, armor_class: 10, max_hp: 60,
      saving_throw_bonuses: { ...template.saving_throw_bonuses, constitution: 0 },
      condition_immunities: [], traits: [], weapon_masteries: [],
    });
    return { combatant_id: id, side, position_ft: position, state: S.buildState(template) };
  } catch (error) {
    console.error("Failed to build start-turn condition combatant", { id, error });
    throw error;
  }
}

function fight() {
  try {
    const attacker = member("renamed-source", "monsters", 0);
    const target = member("renamed-target", "heroes", 5);
    const attack = {
      id: "renamed-bite", weaponId: "renamed-bite", name: "Renamed Bite", kind: "melee",
      bonus: 10, diceCount: 1, diceSize: 4, damageBonus: 0, damageType: "piercing",
      reach: 5, animation: "strike", onHitDamage: [],
      onHitConditionSave: {
        saveAbility: "constitution", dc: 21, conditionId: "poisoned",
        repeatSaveTiming: "target_turn_end", cannotRegainHitPoints: true,
        startOfTurnDamageDiceCount: 6, startOfTurnDamageDiceSize: 6,
        startOfTurnDamageType: "poison",
      },
    };
    attacker.state.template.attacks = [attack];
    attacker.state.template.primary_attack_id = attack.id;
    return { attacker, target, attack, setup: { heroes: [target], monsters: [attacker] } };
  } catch (error) {
    console.error("Failed to build start-turn condition fight", { error });
    throw error;
  }
}

{
  const { attacker, target, attack, setup } = fight();
  setDice([15, 2, 1]);
  const event = A.resolveAttack(1, 1, attacker, target, attack, 5, {
    spendAction: false, setup,
  });
  assert.equal(event.hit, true);
  assert.equal(event.save_succeeded, false);
  const effect = target.state.timed_effects.find((item) => item.effect_id === "poisoned");
  assert.ok(effect);
  assert.equal(effect.cannot_regain_hit_points, true);
  assert.equal(effect.repeat_save_ability, "constitution");
  assert.equal(effect.repeat_save_dc, 21);
  assert.equal(effect.repeat_save_timing, "target_turn_end");
  assert.equal(effect.start_of_turn_dice_count, 6);
  assert.equal(effect.start_of_turn_dice_size, 6);
  assert.equal(effect.start_of_turn_damage_type, "poison");

  const hpBefore = target.state.current_hp;
  setDice([1, 1, 1, 1, 1, 1]);
  const burn = Burn.resolve(2, 2, target, setup);
  assert.equal(burn.events.length, 1);
  assert.equal(target.state.current_hp, hpBefore - 6);
  assert.match(burn.events[0].description, /6 poison damage/);

  setDice([20]);
  const recovered = Lifecycle.resolveTargetTiming(3, 2, target, "target_turn_end", setup);
  assert.equal(recovered.events[0].save_succeeded, true);
  assert.equal(target.state.active_effect_ids.includes("poisoned"), false);
  assert.equal(target.state.timed_effects.length, 0);
}

console.log("Universal on-hit start-turn damage condition lifecycle passed.");
