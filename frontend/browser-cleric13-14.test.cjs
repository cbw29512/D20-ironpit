"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"));

window.IRON_PIT_BROWSER_ROLLS = {
  modeFromSources: () => "normal",
  d20: (bonus) => ({
    natural: 1, total: 1 + bonus, mode: "normal",
    rolls: [1], selected_roll: 1, modifier: bonus, revisions: [],
  }),
};
window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage: (_state, amount) => amount,
  applyDamage: (state, amount) => { state.current_hp = Math.max(0, state.current_hp - amount); return null; },
};
window.IRON_PIT_BROWSER_GRAPPLE = { apply: () => [] };
window.IRON_PIT_BROWSER_CONDITION_RULES = { autoFailStrDex: () => false };
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => Boolean(state[`${cost}_available`]),
  spend: (state, cost) => { state[`${cost}_available`] = false; },
};
window.IRON_PIT_BROWSER_SPELLCASTING = { markSlotSpellCast: () => {} };
window.IRON_PIT_BROWSER_STATE = {
  distance: (a, b) => Math.abs(a.position_ft - b.position_ft),
  sizeAtMost: () => true,
  grantTemporaryHp: (state, amount) => {
    state.temporary_hp = Math.max(state.temporary_hp || 0, amount);
    return state.temporary_hp;
  },
};
window.IRON_PIT_DICE = { rollMany: (count) => Array.from({ length: count }, () => 1) };

load("browser-saves.js");
load("browser-spell-resolution.js");

const caster = {
  combatant_id: "cleric", side: "heroes", position_ft: 0,
  state: {
    current_hp: 73, temporary_hp: 0, is_alive: true, is_dead: false,
    is_unconscious: false, is_stable: false,
    death_save_successes: 0, death_save_failures: 0,
    action_available: true, bonus_action_available: true, reaction_available: true,
    active_effect_ids: [], resources: {},
    template: {
      name: "Seraphine Dawnshield",
      ability_scores: { wisdom: 20 },
      damaging_action_temporary_hp_rider: {
        source_id: "improved-blessed-strikes",
        action_ids: ["sacred-flame"],
        ability: "wisdom",
        multiplier: 2,
      },
    },
  },
};
const target = {
  combatant_id: "target", side: "monsters", position_ft: 30,
  state: {
    current_hp: 30, temporary_hp: 0, is_alive: true, is_dead: false,
    is_unconscious: false, is_stable: false,
    death_save_successes: 0, death_save_failures: 0,
    active_effect_ids: [],
    template: { name: "Target", saving_throw_bonuses: { dexterity: 0 } },
  },
};
const choice = {
  action: {
    id: "sacred-flame", name: "Sacred Flame", level: 0, actionCost: "action",
    range: 60, saveAbility: "dexterity", dc: 18,
    damageDiceCount: 3, damageDiceSize: 8, damageBonus: 5,
    damageType: "radiant", successDamage: "none",
  },
  slotLevel: 0,
  targetIds: ["target"],
  placement: null,
};

const result = window.IRON_PIT_BROWSER_SPELL_RESOLUTION.resolve(
  1, 1, caster, { heroes: [caster], monsters: [target] }, choice, "1:cleric",
);
const rider = result.events.find((event) => event.feature_id === "improved-blessed-strikes");

assert.ok(rider);
assert.equal(caster.state.temporary_hp, 10);
assert.equal(rider.temporary_hp_before, 0);
assert.equal(rider.temporary_hp_after, 10);
assert.equal(target.state.current_hp, 22);

console.log("Browser Improved Blessed Strikes reuses generic post-damage Temporary HP.");
