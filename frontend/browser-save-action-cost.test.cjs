"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-rolls.js", "browser-action-economy.js", "browser-saving-throws.js", "browser-saves.js",
]) load(file);

window.IRON_PIT_DICE = {
  roll: () => 20,
  rollMany: (count) => Array.from({ length: count }, () => 1),
};
window.IRON_PIT_BROWSER_ATTACK = { adjustedDamage: (_state, amount) => amount, applyDamage: () => null };
window.IRON_PIT_BROWSER_GRAPPLE = { apply: () => [] };
window.IRON_PIT_BROWSER_STATE = { sizeAtMost: () => true };
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS = { saveAdvantage: () => 0, saveAdvantageSourceNames: () => [] };
window.IRON_PIT_BROWSER_CONDITION_RULES = { canSee: () => true, autoFailStrDex: () => false, incapacitated: () => false };

const state = () => ({
  template: { name: "Tester", creature_type: "humanoid", saving_throw_bonuses: { wisdom: 0 } },
  resources: {}, active_effect_ids: [], active_modifiers: [],
  action_available: true, bonus_action_available: true, reaction_available: true,
  is_alive: true, is_dead: false, is_unconscious: false,
  current_hp: 10, temporary_hp: 0, death_save_successes: 0, death_save_failures: 0,
});
const actor = { combatant_id: "actor", side: "heroes", state: state() };
const target = { combatant_id: "target", side: "monsters", state: state() };
const action = {
  id: "test-save", name: "Test Save", actionCost: "bonus_action",
  saveAbility: "wisdom", dc: 10, range: 30, damageDiceCount: 0,
};

window.IRON_PIT_BROWSER_SAVES.resolveAction(1, 1, actor, target, action, 5);
assert.equal(actor.state.bonus_action_available, false);
assert.equal(actor.state.action_available, true);

console.log("Browser save-action economy regression passed.");
