"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

let rolls = [];
window.IRON_PIT_BROWSER_ROLLS = {
  modeFromSources: (advantage, disadvantage) => {
    if (Boolean(advantage) === Boolean(disadvantage)) return "normal";
    return advantage ? "advantage" : "disadvantage";
  },
  d20: (modifier, mode) => {
    const count = mode === "normal" ? 1 : 2;
    const used = rolls.splice(0, count);
    const selected = mode === "advantage" ? Math.max(...used)
      : mode === "disadvantage" ? Math.min(...used) : used[0];
    return {
      notation: "1d20", rolls: used, modifier, selected_roll: selected,
      total: selected + modifier, mode, revisions: [],
    };
  },
};
window.IRON_PIT_BROWSER_ATTACK = { adjustedDamage: (_state, amount) => amount, applyDamage: () => null };
window.IRON_PIT_BROWSER_GRAPPLE = { apply: () => [] };
window.IRON_PIT_BROWSER_STATE = { sizeAtMost: () => true };
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS = {
  saveAdvantage: () => 0, saveAdvantageSourceNames: () => [],
  saveDisadvantage: () => 0, consumeSavingThrowModifiers: () => {},
};
window.IRON_PIT_BROWSER_CONDITION_RULES = { canSee: () => true, autoFailStrDex: () => false };
window.IRON_PIT_BROWSER_MODIFIERS = {
  savingThrowFlat: () => 0, applyD20Bonus: (_state, _kind, roll) => roll,
};
window.IRON_PIT_BROWSER_EXHAUSTION = { saveDisadvantage: () => 0 };
window.IRON_PIT_DICE = { roll: () => 1, rollMany: () => [] };

for (const file of [
  "browser-action-economy.js", "browser-saving-throws.js", "browser-saves.js",
]) load(file);

const state = (creatureType) => ({
  template: {
    name: "Target", creature_type: creatureType,
    saving_throw_bonuses: { constitution: 0 },
  },
  resources: {}, active_effect_ids: [], active_modifiers: [], active_d20_bonus_dice: [],
  action_available: true, bonus_action_available: true, reaction_available: true,
  is_alive: true, is_dead: false, current_hp: 10, temporary_hp: 0,
  death_save_successes: 0, death_save_failures: 0,
});
const actor = { combatant_id: "actor", side: "heroes", state: state("humanoid") };
const action = {
  id: "typed-save", name: "Typed Save", saveAbility: "constitution",
  dc: 15, range: 60, damageDiceCount: 0,
  saveDisadvantageCreatureTypes: ["construct"],
};

rolls = [18, 4];
let target = { combatant_id: "construct", side: "monsters", state: state("Construct") };
let event = window.IRON_PIT_BROWSER_SAVES.resolveAction(
  1, 1, actor, target, action, 30, { spendAction: false },
);
assert.equal(event.saving_throw_roll.mode, "disadvantage");
assert.equal(event.saving_throw_roll.selected_roll, 4);
assert.match(event.description, /Typed Save imposes Disadvantage/);

rolls = [18];
target = { combatant_id: "humanoid", side: "monsters", state: state("humanoid") };
event = window.IRON_PIT_BROWSER_SAVES.resolveAction(
  2, 1, actor, target, action, 30, { spendAction: false },
);
assert.equal(event.saving_throw_roll.mode, "normal");
assert.equal(event.saving_throw_roll.selected_roll, 18);

console.log("Creature-type saving-throw Disadvantage browser parity passed.");
