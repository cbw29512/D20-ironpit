"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
let rolls = [];
window.IRON_PIT_DICE = {
  roll: (sides) => {
    const value = rolls.shift();
    if (!Number.isInteger(value) || value < 1 || value > sides) throw new Error("Invalid die.");
    return value;
  },
  rollMany: (count, sides) => Array.from({ length: count }, () => window.IRON_PIT_DICE.roll(sides)),
};
window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage: (_state, total) => total,
  applyDamage: (state, total) => { state.current_hp -= total; return "damaged"; },
};
for (const name of [
  "browser-modifier-validation.js", "browser-modifiers.js",
  "browser-rolls.js", "browser-damage-defense-rules.js", "browser-hit-damage.js",
  "browser-action-economy.js", "browser-condition-rules.js",
  "browser-timed-conditions.js", "browser-timed-condition-lifecycle.js",
  "browser-spellcasting.js", "browser-spell-modifiers.js",
  "browser-timed-self-buff-policy.js", "browser-timed-self-buffs.js",
  "browser-precombat-buffs.js",
]) load(name);

const bonus = {
  kind: "bonus-damage", diceCount: 3, diceSize: 6,
  damageType: "radiant", requiredWeaponAttackKind: "melee",
};
const action = {
  id: "slot-melee-bonus-slot-1", name: "Slot Melee Bonus (Level 1)",
  actionCost: "bonus_action", resourceId: "spell-slot-1", resourceCost: 1,
  expendSlotWithoutCast: true, openingEligible: false,
  durationRounds: 1, expiryTiming: "source_turn_end",
  modifierEffects: [bonus], conditionIds: [], damageResistances: [],
  animation: "radiant-buff",
};
const state = {
  template: { name: "Test Caster", ruleset: "2014", traits: [], brutal_critical_dice: 0, timed_self_buff_actions: [action] },
  feature_last_turn_keys: {},
  action_available: true, bonus_action_available: true,
  current_hp: 50, is_alive: true, is_dead: false,
  active_modifiers: [], timed_effects: [], active_effect_ids: [],
  resources: { "spell-slot-1": 1 },
  spell_slot_expended_turn_key: "1:caster",
};
const caster = { combatant_id: "caster", side: "heroes", state };
const enemy = {
  combatant_id: "target", side: "monsters",
  state: { template: { name: "Target", max_hp: 100 }, current_hp: 100,
    temporary_hp: 0, active_modifiers: [], timed_effects: [], active_effect_ids: [] },
};
const setup = { heroes: [caster], monsters: [enemy] };

assert.equal(window.IRON_PIT_BROWSER_PRECOMBAT_BUFFS.timedChoice(caster, setup), null);
assert.equal(window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS.choose(caster, setup, "action", "1:caster")?.id, action.id);
const activation = window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS.resolve(
  1, 1, caster, action, { setup, turnKey: "1:caster", affectedStates: [state, enemy.state] },
);
assert.equal(activation.feature_id, action.id);
assert.equal(state.resources["spell-slot-1"], 0);
assert.equal(state.bonus_action_available, false);
assert.equal(state.action_available, true);
assert.equal(state.spell_slot_expended_turn_key, "1:caster");
assert.equal(state.active_modifiers[0].required_weapon_attack_kind, "melee");

const weapon = {
  id: "mace", name: "Mace", kind: "melee", diceCount: 1, diceSize: 6,
  damageBonus: 0, damageType: "bludgeoning", onHitDamage: [],
};
assert.equal(window.IRON_PIT_BROWSER_MODIFIERS.bonusDamage(state, "target", weapon).length, 1);
assert.equal(window.IRON_PIT_BROWSER_MODIFIERS.bonusDamage(state, "target", { ...weapon, kind: "ranged" }).length, 0);
assert.equal(window.IRON_PIT_BROWSER_MODIFIERS.bonusDamage(state, "target").length, 0);

rolls = [4, 2, 3, 5];
const melee = window.IRON_PIT_BROWSER_HIT_DAMAGE.resolve(
  state, enemy.state, weapon, false, "normal", "1:caster",
  { targetId: "target", affectedStates: [state, enemy.state] },
);
assert.deepEqual(melee.damageComponents.find((x) => x.source === action.name)?.rolls, [2, 3, 5]);

rolls = [4];
const ranged = window.IRON_PIT_BROWSER_HIT_DAMAGE.resolve(
  state, enemy.state, { ...weapon, kind: "ranged", id: "bow" }, false,
  "normal", "1:caster", { targetId: "target", affectedStates: [state, enemy.state] },
);
assert.equal(ranged.damageComponents.some((x) => x.source === action.name), false);
const timed = state.timed_effects.find((x) => x.source_effect_id === action.id);
assert.ok(timed);
window.IRON_PIT_BROWSER_TIMED.removeGroup(state, timed);
assert.equal(state.active_modifiers.length, 0);
console.log("Slot-funded melee-only bonus and non-cast parity passed.");
