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
  "browser-monsters-2014.js", "browser-rolls.js", "browser-action-economy.js",
  "browser-saving-throws.js", "browser-save-immunity.js", "browser-save-action-support.js",
  "browser-save-action-attempt.js", "browser-save-damage.js", "browser-save-damage-legacy.js",
  "browser-save-damage-apply.js", "browser-save-action-effects.js", "browser-save-event.js",
  "browser-saves.js",
]) load(file);

const pitFiend = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-pit-fiend"];
const fireball = pitFiend.spell_save_actions.find((item) => item.id === "fireball");
assert.ok(fireball);
assert.equal(fireball.dc, 21);
assert.equal(fireball.range, 150);
assert.equal(fireball.damageDiceCount, 8);
assert.equal(fireball.damageDiceSize, 6);
assert.equal(fireball.damageType, "fire");
assert.equal(fireball.successDamage, "half");
assert.equal(fireball.area.shape, "radius");
assert.equal(fireball.area.radius_ft, 20);
assert.equal(pitFiend.resources.fireball, undefined);

window.IRON_PIT_DICE = {
  roll: () => 20,
  rollMany: (count) => Array.from({ length: count }, () => 6),
};
window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES = {
  resolveDamage: (_state, amount) => ({ applied: amount, healed: 0, sourceName: null }),
};
window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage: (_state, amount) => amount,
  applyDamage: (state, amount) => { state.current_hp -= amount; return null; },
};
window.IRON_PIT_BROWSER_GRAPPLE = { apply: () => [] };
window.IRON_PIT_BROWSER_STATE = { sizeAtMost: () => true };
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS = {
  saveAdvantage: () => 0, saveAdvantageSourceNames: () => [],
};
window.IRON_PIT_BROWSER_CONDITION_RULES = {
  canSee: () => true, autoFailStrDex: () => false, incapacitated: () => false,
};

const actor = {
  combatant_id: "pit-fiend", side: "monsters",
  state: {
    template: pitFiend, resources: { ...pitFiend.resources }, active_effect_ids: [],
    active_modifiers: [], action_available: true, bonus_action_available: true,
    reaction_available: true, is_alive: true, is_dead: false, is_unconscious: false,
    current_hp: pitFiend.max_hp, temporary_hp: 0,
    death_save_successes: 0, death_save_failures: 0,
  },
};
const target = {
  combatant_id: "target", side: "heroes",
  state: {
    template: {
      name: "Target", creature_type: "humanoid",
      saving_throw_bonuses: { dexterity: 1 }, condition_immunities: [],
    },
    resources: {}, active_effect_ids: [], active_modifiers: [],
    action_available: true, bonus_action_available: true, reaction_available: true,
    is_alive: true, is_dead: false, is_unconscious: false,
    current_hp: 100, temporary_hp: 0,
    death_save_successes: 0, death_save_failures: 0,
  },
};

const event = window.IRON_PIT_BROWSER_SAVES.resolveAction(
  1, 1, actor, target, fireball, 100,
);
assert.equal(event.save_succeeded, true);
assert.equal(event.damage_roll.total, 24);
assert.equal(target.state.current_hp, 76);
assert.equal(actor.state.action_available, false);
assert.equal(actor.state.resources.fireball, undefined);

console.log("2014 innate Fireball browser binding and resolution regression passed.");
