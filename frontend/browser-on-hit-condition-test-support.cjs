"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => {
  try {
    return vm.runInThisContext(
      fs.readFileSync(path.join(__dirname, name), "utf8"),
      { filename: name },
    );
  } catch (error) {
    console.error("Failed to load on-hit condition test dependency", { name, error });
    throw error;
  }
};

if (!window.IRON_PIT_BROWSER_STATE) {
  for (const file of [
    "browser-heroes.js", "browser-monsters-2014.js", "browser-condition-immunity.js",
    "browser-condition-rules.js", "browser-action-economy.js", "browser-grapple.js",
    "browser-modifier-validation.js", "browser-modifiers.js", "browser-state.js",
    "browser-rage.js", "browser-sneak-attack.js", "browser-rolls.js",
    "browser-undead-fortitude.js", "browser-terminal-effects.js", "browser-zero-hp.js",
    "browser-timed-conditions.js", "browser-weapon-mastery.js", "browser-ability-hooks.js",
    "browser-attack-outcome.js", "browser-attack.js", "browser-saving-throws.js",
    "browser-creature-kind.js", "browser-on-hit-condition-lifecycle.js",
    "browser-on-hit-condition-save.js", "browser-saves.js", "browser-condition-lifecycle.js",
  ]) load(file);
}
if (!window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS) load("browser-source-bound-effects.js");

const S = window.IRON_PIT_BROWSER_STATE;
const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];
const attackShape = {
  id: "greatsword-attack", weaponId: "greatsword", name: "Greatsword", kind: "melee",
  bonus: 5, diceCount: 2, diceSize: 6, damageBonus: 3, damageType: "slashing",
  reach: 5, animation: "slash", attackAbility: "strength",
  attackAbilityModifier: 3, onHitDamage: [],
};

function dice(values) {
  try {
    const rolls = [...values];
    window.IRON_PIT_DICE = {
      roll(sides) {
        const value = rolls.shift();
        if (!(value >= 1 && value <= sides)) throw new Error("invalid d" + sides + ": " + value);
        return value;
      },
      rollMany(count, sides) {
        return Array.from({ length: count }, () => this.roll(sides));
      },
    };
  } catch (error) {
    console.error("Failed to configure on-hit condition test dice", { error });
    throw error;
  }
}

function member(id, side, options = {}) {
  try {
    const template = structuredClone(base);
    Object.assign(template, {
      id: "template-" + id, name: id, level: 1, armor_class: options.armorClass ?? 10,
      max_hp: 40, attacks: [structuredClone(attackShape)], primary_attack_id: attackShape.id,
      weapon_masteries: [], traits: [], size: options.size || "medium",
      creature_type: options.creatureType || template.creature_type,
      condition_immunities: options.immune || [],
      saving_throw_bonuses: { ...template.saving_throw_bonuses, constitution: 0, strength: 0 },
    });
    if (options.onHitConditionSave) {
      template.attacks[0].onHitConditionSave = options.onHitConditionSave;
    }
    return {
      combatant_id: id, side, position_ft: options.position ?? 0,
      state: S.buildState(template),
    };
  } catch (error) {
    console.error("Failed to build on-hit condition test member", { id, error });
    throw error;
  }
}

function attack(attacker, target, values) {
  try {
    dice(values);
    return window.IRON_PIT_BROWSER_ATTACK.resolveAttack(
      1, 1, attacker, target, attacker.state.template.attacks[0], 5,
      { spendAction: false },
    );
  } catch (error) {
    console.error("Failed on-hit condition browser test attack", { error });
    throw error;
  }
}

module.exports = { assert, attack, dice, member };
