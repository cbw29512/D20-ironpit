"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

const saveRolls = [1, 20];
let damageRollCalls = 0;
window.IRON_PIT_BROWSER_ROLLS = {
  modeFromSources: () => "normal",
  bloodiedSaveAdvantage: () => 0,
  d20: (bonus) => {
    const natural = saveRolls.shift();
    return { total: natural + bonus, mode: "normal", rolls: [natural], modifier: bonus, selected_roll: natural };
  },
};
window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage: (_state, amount) => amount,
  applyDamage: (state, amount) => {
    state.current_hp = Math.max(0, state.current_hp - amount);
    if (state.current_hp === 0) { state.is_alive = false; state.is_dead = true; }
    return state.is_dead ? "dead" : "damaged";
  },
};
window.IRON_PIT_BROWSER_GRAPPLE = { apply: () => [] };
window.IRON_PIT_BROWSER_STATE = { sizeAtMost: () => true };
window.IRON_PIT_BROWSER_CONDITION_RULES = {
  autoFailStrDex: () => false,
  incapacitated: () => false,
  has: () => false,
};
window.IRON_PIT_ACTION_ECONOMY = { available: () => true, spend: () => {} };
window.IRON_PIT_DICE = {
  rollMany: () => {
    damageRollCalls += 1;
    if (damageRollCalls > 1) throw new Error("Death Burst damage rolled more than once.");
    return [6, 6];
  },
};

load("browser-grid-geometry.js");
load("browser-saves.js");
load("browser-death-triggers.js");

const member = (id, x, side, hp = 20) => ({
  combatant_id: id,
  side,
  position_ft: x * 5,
  state: {
    current_hp: hp,
    temporary_hp: 0,
    is_alive: hp > 0,
    is_dead: hp <= 0,
    is_unconscious: false,
    is_stable: false,
    death_save_successes: 0,
    death_save_failures: 0,
    active_effect_ids: [],
    resources: {},
    position: { x, y: 0 },
    template: { name: id, size: "medium", saving_throw_bonuses: { dexterity: 0 } },
  },
});
const source = member("magma", 0, "monsters", 0);
source.state.template.death_trigger_effects = [{
  id: "death-burst", name: "Death Burst", radius_ft: 5, save_ability: "dexterity", dc: 11,
  damage_dice_count: 2, damage_dice_size: 6, damage_bonus: 0, damage_type: "fire", half_damage_on_success: true,
}];
const first = member("first", 1, "heroes"), second = member("second", 1, "heroes");
const setup = { heroes: [first, second], monsters: [source] };
const resolved = new Set();

const result = window.IRON_PIT_BROWSER_DEATH_TRIGGERS.resolve(10, 2, source, setup, resolved);
assert.equal(result.sequence, 12);
assert.equal(result.events.length, 2);
assert.equal(result.events[0].feature_id, "death-burst");
assert.equal(result.events[0].save_succeeded, false);
assert.equal(result.events[1].save_succeeded, true);
assert.deepEqual(result.events[0].damage_components[0].rolls, [6, 6]);
assert.deepEqual(result.events[1].damage_components[0].rolls, [6, 6]);
assert.equal(result.events[0].damage_components[0].total, 12);
assert.equal(result.events[1].damage_components[0].total, 6);
assert.equal(damageRollCalls, 1);

const again = window.IRON_PIT_BROWSER_DEATH_TRIGGERS.resolve(result.sequence, 2, source, setup, resolved);
assert.deepEqual(again.events, []);
assert.equal(again.sequence, result.sequence);
console.log("Browser universal Death Burst shared-roll and once-only parity passed.");
