"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"));

const saveRolls = [1, 20];
let damageRollCalls = 0;
window.IRON_PIT_BROWSER_ROLLS = {
  modeFromSources: () => "normal",
  d20: (bonus) => {
    const natural = saveRolls.shift();
    return { natural, total: natural + bonus, mode: "normal", rolls: [natural], modifier: bonus };
  },
};
window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage: (_state, amount) => amount,
  applyDamage: (state, amount) => { state.current_hp -= amount; return null; },
};
window.IRON_PIT_BROWSER_GRAPPLE = { apply: () => [] };
window.IRON_PIT_BROWSER_STATE = {
  distance: (a, b) => Math.abs(a.position_ft - b.position_ft),
  sizeAtMost: () => true,
};
window.IRON_PIT_BROWSER_CONDITION_RULES = { autoFailStrDex: () => false, has: () => false };
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => Boolean(state[`${cost}_available`]),
  spend: (state, cost) => { state[`${cost}_available`] = false; },
};
window.IRON_PIT_BROWSER_SPELLCASTING = { markSlotSpellCast: () => {} };
window.IRON_PIT_DICE = {
  rollMany: () => {
    damageRollCalls += 1;
    if (damageRollCalls > 1) throw new Error("Simultaneous save damage was rolled more than once.");
    return [4, 4];
  },
};

load("browser-saves.js");
load("browser-spell-resolution.js");

const member = (id, side, position) => ({
  combatant_id: id,
  side,
  position_ft: position,
  state: {
    current_hp: 20,
    is_alive: true,
    is_dead: false,
    is_unconscious: false,
    is_stable: false,
    death_save_successes: 0,
    death_save_failures: 0,
    action_available: true,
    bonus_action_available: true,
    reaction_available: true,
    active_effect_ids: [],
    resources: {},
    template: { name: id, saving_throw_bonuses: { dexterity: 0 } },
  },
});
const caster = member("caster", "heroes", 0);
const targets = [member("target-1", "monsters", 30), member("target-2", "monsters", 30)];
const choice = {
  action: {
    id: "shared-flame", name: "Shared Flame", level: 0, actionCost: "action",
    range: 60, areaRadius: 10, saveAbility: "dexterity", dc: 10,
    damageDiceCount: 2, damageDiceSize: 6, damageBonus: 0,
    damageType: "fire", successDamage: "half", upcastDicePerLevel: 0,
  },
  slotLevel: 0,
  targetIds: targets.map((target) => target.combatant_id),
  placement: { enemyIds: targets.map((target) => target.combatant_id), friendlyIds: [] },
};
const result = window.IRON_PIT_BROWSER_SPELL_RESOLUTION.resolve(
  1, 1, caster, { heroes: [caster], monsters: targets }, choice, "caster:round-1",
);
const saves = result.events.filter((event) => event.event_type === "saving_throw");

assert.equal(damageRollCalls, 1);
assert.equal(saves.length, 2);
assert.equal(saves[0].save_succeeded, false);
assert.equal(saves[1].save_succeeded, true);
assert.deepEqual(saves[0].damage_components[0].rolls, [4, 4]);
assert.deepEqual(saves[1].damage_components[0].rolls, [4, 4]);
assert.equal(saves[0].damage_roll.total, 8);
assert.equal(saves[1].damage_roll.total, 4);
console.log("Browser simultaneous save damage uses one shared RAW damage roll.");
