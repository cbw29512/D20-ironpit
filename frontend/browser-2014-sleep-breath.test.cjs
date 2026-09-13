"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "action" ? state.action_available : true,
  spend: (state, cost) => { if (cost === "action") state.action_available = false; },
};
window.IRON_PIT_BROWSER_SPELLCASTING = {
  slotSpellAvailable: () => true,
  markSlotSpellCast: () => {},
};
window.IRON_PIT_BROWSER_TIMED = {
  removeGroup: (state, effect) => {
    state.timed_effects = state.timed_effects.filter((item) => item !== effect);
    if (!state.timed_effects.some((item) => item.effect_id === effect.effect_id)) {
      state.active_effect_ids = state.active_effect_ids.filter((id) => id !== effect.effect_id);
      return [effect.effect_id];
    }
    return [];
  },
};
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_STATE = { effectiveMaxHp: (state) => state.template.max_hp };
window.IRON_PIT_BROWSER_CONCENTRATION = null;
window.IRON_PIT_BROWSER_UNDEAD_FORTITUDE = null;
load("browser-source-bound-effects.js");
load("browser-condition-removal.js");
load("browser-zero-hp.js");

function combatant(id, side) {
  return {
    combatant_id: id, side, position_ft: side === "heroes" ? 5 : 10,
    state: {
      action_available: true, is_alive: true, is_dead: false, is_unconscious: false, is_stable: false,
      current_hp: 20, temporary_hp: 0, death_save_failures: 0,
      active_effect_ids: [], timed_effects: [], resources: {}, concentration: null,
      template: { name: id, kind: side === "heroes" ? "character" : "monster", max_hp: 20, condition_removal_actions: [], traits: [] },
    },
  };
}

const ally = combatant("ally", "heroes");
const sleeper = combatant("sleeper", "heroes");
sleeper.position_ft = 5;
sleeper.state.active_effect_ids = ["unconscious"];
sleeper.state.timed_effects = [{
  effect_id: "unconscious", source_id: "dragon", source_effect_id: "sleep-breath",
  allowed_removal_action_ids: ["wake-sleeper"], ends_on_damage: true,
}];
const setup = { heroes: [ally, sleeper], monsters: [] };

const choice = window.IRON_PIT_BROWSER_CONDITION_REMOVAL.chooseAction(ally, setup, "1:ally");
assert.equal(choice.action.id, "wake-sleeper");
assert.equal(choice.target, sleeper);
window.IRON_PIT_BROWSER_CONDITION_REMOVAL.resolve(1, 1, ally, sleeper, choice.action, choice.conditions, "1:ally");
assert.equal(ally.state.action_available, false);
assert.deepEqual(sleeper.state.active_effect_ids, []);

const damaged = combatant("damaged", "heroes");
damaged.state.active_effect_ids = ["unconscious"];
damaged.state.timed_effects = [{
  effect_id: "unconscious", source_id: "dragon", source_effect_id: "sleep-breath",
  allowed_removal_action_ids: ["wake-sleeper"], ends_on_damage: true,
}];
assert.equal(window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(damaged.state, 1), "damaged");
assert.equal(damaged.state.current_hp, 19);
assert.deepEqual(damaged.state.active_effect_ids, []);
assert.deepEqual(damaged.state.timed_effects, []);

const ordinary = combatant("ordinary", "heroes");
ordinary.state.active_effect_ids = ["unconscious"];
ordinary.state.timed_effects = [{ effect_id: "unconscious", source_id: "other", allowed_removal_action_ids: [] }];
assert.equal(window.IRON_PIT_BROWSER_CONDITION_REMOVAL.chooseAction(ally, { heroes: [ally, ordinary], monsters: [] }, "1:ally"), null);

console.log("2014 browser Sleep Breath regressions passed.");
