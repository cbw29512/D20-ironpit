"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

window.IRON_PIT_BROWSER_ROLLS = {
  modeFromSources: () => "normal",
  d20: (bonus) => ({ natural: 1, total: 1 + bonus, mode: "normal", rolls: [1], modifier: bonus }),
};
window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage: (state, amount, type) => state.template.damage_resistances?.includes(type) ? Math.floor(amount / 2) : amount,
  applyDamage: (state, amount) => { state.current_hp -= amount; return null; },
};
window.IRON_PIT_BROWSER_GRAPPLE = { apply: () => [] };
window.IRON_PIT_BROWSER_STATE = { sizeAtMost: () => true };
window.IRON_PIT_BROWSER_CONDITION_RULES = { autoFailStrDex: () => false };
window.IRON_PIT_ACTION_ECONOMY = {
  available: () => true,
  spend: () => {},
};
window.IRON_PIT_DICE = {
  rollMany: (count, size) => {
    assert.equal(count, 1);
    assert.equal(size, 6);
    return window.__rolls.shift();
  },
};
window.__rolls = [[6], [4]];

load("browser-save-damage.js");
load("browser-saves.js");

const actor = { combatant_id: "actor", state: { resources: {}, template: { name: "Actor" } } };
const target = {
  combatant_id: "target",
  state: {
    current_hp: 20, temporary_hp: 0, is_alive: true, is_dead: false, is_unconscious: false,
    is_stable: false, death_save_successes: 0, death_save_failures: 0, active_effect_ids: [],
    template: { name: "Target", saving_throw_bonuses: { dexterity: 0 }, damage_resistances: ["fire"] },
  },
};
const action = {
  id: "split-save", name: "Split Save", saveAbility: "dexterity", dc: 40, range: 60,
  successDamage: "half", magicalEffect: true,
  damageDiceCount: 0, damageBonus: 0, damageType: null,
  damageComponents: [
    { diceCount: 1, diceSize: 6, damageBonus: 0, damageType: "fire" },
    { diceCount: 1, diceSize: 6, damageBonus: 0, damageType: "radiant" },
  ],
};

const event = window.IRON_PIT_BROWSER_SAVES.resolveAction(1, 1, actor, target, action, 30);

assert.equal(event.save_succeeded, false);
assert.deepEqual(event.damage_components.map((part) => [part.damage_type, part.total, part.applied_total]), [
  ["fire", 6, 3],
  ["radiant", 4, 4],
]);
assert.equal(event.damage_roll.total, 7);
assert.equal(target.state.current_hp, 13);
console.log("Browser multi-component save damage parity passed.");
