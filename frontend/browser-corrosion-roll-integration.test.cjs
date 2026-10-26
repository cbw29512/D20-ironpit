"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs"), vm = require("node:vm"), path = require("node:path");
global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
load("browser-weapon-corrosion.js");
load("browser-weapon-corrosion-roll.js");
load("browser-rolls.js");
const queued = (values) => {
  const queue = [...values];
  window.IRON_PIT_DICE = {
    rollMany: (count) => Array.from({length: count}, () => queue.shift()),
    roll: () => queue.shift(),
  };
};
const attack = Object.freeze({
  id: "blade", weaponId: "blade", name: "Sword", kind: "melee",
  diceCount: 1, diceSize: 8, damageBonus: 3, damageType: "slashing",
  onHitDamage: [{source: "Acid rider", diceCount: 1, diceSize: 6, damageBonus: 0, damageType: "acid"}],
});
const state = (penalties) => ({
  template: {traits: []}, feature_last_turn_keys: {},
  weapon_corrosion_penalties: penalties,
});
queued([6, 4]);
const clean = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(state({}), attack, false, "normal", "1:hero");
queued([6, 4]);
const damaged = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(state({blade: 2}), attack, false, "normal", "1:hero");
assert.equal(damaged.components[0].total, clean.components[0].total - 2);
assert.equal(damaged.components[1].total, 4);
assert.deepEqual(damaged.components[1].rolls, clean.components[1].rolls);
assert.equal(damaged.roll.total, clean.roll.total - 2);
assert.match(damaged.components[0].notation, /corrosion -2/);
queued([1, 4]);
const clamped = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(state({blade: 4}), attack, false, "normal", "2:hero");
assert.equal(clamped.components[0].total, 0);
assert.equal(clamped.components[1].total, 4);
queued([6, 4]);
assert.equal(window.IRON_PIT_BROWSER_ROLLS.weaponDamage(state({unrelated: 2}), attack, false, "normal", "3:hero").roll.total, clean.roll.total);
queued([6, 4]);
assert.throws(() => window.IRON_PIT_BROWSER_ROLLS.weaponDamage(state({blade: 5}), attack, false, "normal", "4:hero"), /Destroyed weapon/);
assert.equal(attack.damageBonus, 3);
console.log("Universal base-weapon corrosion applies to damage only, preserving riders.");
