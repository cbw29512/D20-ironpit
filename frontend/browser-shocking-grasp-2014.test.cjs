"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES = {
  resolveDamage: (state, amount, type, allowVulnerability = true, sourceQualifiers = [], ignoreResistance = false) => ({
    applied: window.IRON_PIT_BROWSER_ATTACK?.adjustedDamage
      ? window.IRON_PIT_BROWSER_ATTACK.adjustedDamage(state, amount, type, allowVulnerability, sourceQualifiers, ignoreResistance)
      : amount,
    healed: 0,
    sourceName: null,
  }),
};
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);
for (const file of [
  "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-timed-conditions.js", "browser-grapple.js", "browser-modifier-validation.js", "browser-modifiers.js", "browser-state.js",
  "browser-rage.js", "browser-rolls.js", "browser-undead-fortitude.js", "browser-zero-hp.js",
  "browser-attack-outcome.js", "browser-attack.js", "browser-saving-throws.js", "browser-saves.js",
  "browser-spellcasting.js", "browser-spell-modifiers.js", "browser-spell-attack.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const E = window.IRON_PIT_ACTION_ECONOMY;
const A = window.IRON_PIT_BROWSER_SPELL_ATTACK;
const T = window.IRON_PIT_BROWSER_TIMED;

const shockingGrasp = {
  id: "shocking-grasp", name: "Shocking Grasp", level: 0, actionCost: "action",
  attackKind: "melee", range: 5, attackBonus: 5,
  damageDiceCount: 1, damageDiceSize: 8, damageBonus: 0, damageType: "lightning",
  advantageIfTargetWearingMetalArmor: true,
  onHitModifierEffects: [],
  onHitTimedEffects: [{
    effectId: "reaction-suppressed", durationRounds: 1, expiryTiming: "source_turn_start",
    suppressAction: false, suppressBonusAction: false, suppressReactions: true,
    suppressMovement: false, nextAttackDisadvantage: false, sourceIsMagical: true,
  }],
};

function member(id, side, position, extra = {}) {
  const template = {
    id: `template-${id}`, name: id, kind: "character", ruleset: "2014", size: "medium",
    armor_class: extra.armorClass || 10, max_hp: 30, speed_ft: 30,
    movement_modes: { walk_ft: 30, fly_ft: 0, climb_ft: 0, swim_ft: 0, burrow_ft: 0, hover: false },
    saving_throw_bonuses: {}, skill_bonuses: {}, resources: {},
    spell_attack_actions: extra.spells || [],
    damage_immunities: [], damage_resistances: [], damage_vulnerabilities: [],
    condition_immunities: [], wearing_metal_armor: Boolean(extra.metalArmor),
    critical_hit_minimum: 20, traits: [],
  };
  return { combatant_id: id, side, position_ft: position, state: S.buildState(template) };
}

const caster = member("nyra", "heroes", 0, { spells: [shockingGrasp] });
const target = member("karnok", "monsters", 5, { armorClass: 16, metalArmor: true });
const setup = { heroes: [caster], monsters: [target] };
const queue = [1, 15, 4];
window.IRON_PIT_DICE = {
  roll: (sides) => {
    const value = queue.shift();
    if (value == null || value < 1 || value > sides) throw new Error(`invalid fixed d${sides}: ${value}`);
    return value;
  },
  rollMany: (count, sides) => Array.from({ length: count }, () => window.IRON_PIT_DICE.roll(sides)),
};

const event = A.resolve(1, 1, caster, target, shockingGrasp, setup, "1:nyra");
assert.equal(event.attack_roll.mode, "advantage");
assert.deepEqual(event.attack_roll.rolls, [1, 15]);
assert.equal(event.hit, true);
assert.deepEqual(event.applied_condition_ids, ["reaction-suppressed"]);
assert.equal(E.available(target.state, "reaction"), false);

let expiry = T.expireSourceStart(2, 1, caster, setup);
assert.equal(expiry.events.length, 0);
assert.equal(E.available(target.state, "reaction"), false);

expiry = T.expireSourceStart(2, 2, caster, setup);
assert.equal(expiry.events.length, 1);
assert.equal(target.state.active_effect_ids.includes("reaction-suppressed"), false);
assert.equal(E.available(target.state, "reaction"), true);

console.log("Browser 2014 Shocking Grasp regression passed.");
