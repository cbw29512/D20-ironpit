"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(`frontend/${name}`, "utf8"), { filename: name });

window.IRON_PIT_BROWSER_GRID_GEOMETRY = {
  inBounds: () => true,
  overlaps: (a, _as, b, _bs) => a.x === b.x && a.y === b.y,
  footprintDistanceFt: (a, _as, b, _bs) => Math.max(Math.abs(a.x - b.x), Math.abs(a.y - b.y)) * 5,
};
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state) => state.action_available,
  spend: (state) => { state.action_available = false; },
};
window.IRON_PIT_BROWSER_SPELLCASTING = {
  markSlotSpellCast: (state, turnKey) => { state.spell_slot_expended_turn_key = turnKey; },
};
window.IRON_PIT_BROWSER_SAVES = {
  resolveSavingThrow: () => ({ roll: { total: 1, rolls: [1], modifier: 0, selected_roll: 1 }, succeeded: false }),
};
window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage: (_state, amount) => amount,
  applyDamage: (state, amount) => {
    state.current_hp = Math.max(0, state.current_hp - amount);
    if (state.current_hp === 0) { state.is_dead = true; state.is_alive = false; }
  },
};
load("browser-persistent-hazards.js");
const H = window.IRON_PIT_BROWSER_PERSISTENT_HAZARDS;

const caster = {
  combatant_id: "caster", side: "heroes", position_ft: 0,
  state: {
    template: { name: "Caster", size: "medium" }, position: { x: 1, y: 1 },
    resources: { "spell-slot-4": 1 }, action_available: true,
  },
};
const target = {
  combatant_id: "target", side: "monsters", position_ft: 0,
  state: {
    template: { name: "Target", size: "medium" }, position: { x: 8, y: 1 },
    current_hp: 100, is_dead: false, is_alive: true, is_unconscious: false,
  },
};
const setup = {
  heroes: [caster], monsters: [target],
  map_definition: { width_squares: 24, height_squares: 16 },
  persistent_hazards: [],
};
const action = {
  id: "test-hazard", name: "Test Hazard", level: 4, actionCost: "action",
  castRangeFt: 30, durationRounds: 4800, footprintSize: "large",
  triggerRadiusFt: 10, saveAbility: "dexterity", dc: 15,
  failureDamage: 20, successDamage: 10, damageType: "radiant",
  maxTotalDamage: 60, animation: "persistent-hazard",
};

const cast = H.cast(1, 1, caster, setup, action, { x: 6, y: 1 }, "1:caster");
assert.equal(cast.sequence, 2);
assert.equal(setup.persistent_hazards.length, 1);
assert.equal(caster.state.resources["spell-slot-4"], 0);
target.state.position = { x: 7, y: 1 };
const first = H.resolveEntries(2, 1, target, setup, "1:target");
assert.equal(first.events.length, 1);
assert.equal(first.events[0].damage_roll.total, 20);
assert.equal(target.state.current_hp, 80);
assert.equal(setup.persistent_hazards[0].remainingDamageCapacity, 40);
const sameTurn = H.resolveEntries(first.sequence, 1, target, setup, "1:target");
assert.deepEqual(sameTurn.events, []);

H.resolveEntries(sameTurn.sequence, 2, target, setup, "2:target");
H.resolveEntries(sameTurn.sequence + 1, 3, target, setup, "3:target");
assert.equal(setup.persistent_hazards.length, 0);

console.log("Universal browser persistent-hazard regressions passed.");
