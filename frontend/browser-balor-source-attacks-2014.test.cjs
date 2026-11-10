"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
function load(name) {
  vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
}
load("browser-rolls.js");
const values = Array(40).fill(2);
window.IRON_PIT_DICE = {
  roll(sides) {
    const value = values.shift();
    if (!Number.isInteger(value) || value < 1 || value > sides) throw new Error("Invalid test die");
    return value;
  },
  rollMany(count, sides) { return Array.from({ length: count }, () => this.roll(sides)); },
};
const source = {
  template: { name: "Renamed source", traits: [], brutal_critical_dice: 0 },
  active_modifiers: [], feature_last_turn_keys: {}, feature_use_counts: {},
};
const longsword = {
  id: "triple-test", name: "Any Name", kind: "melee", diceCount: 3,
  diceSize: 8, damageBonus: 8, damageType: "slashing",
  criticalDiceMultiplier: 3, onHitDamage: [
    { source: "Same Hit", diceCount: 3, diceSize: 8, damageBonus: 0, damageType: "lightning" },
  ],
};
const roll = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(
  source, longsword, true, "normal", "1:source",
);
assert.deepEqual(roll.components.map((part) => part.rolls.length), [9, 9]);
assert.deepEqual(roll.components.map((part) => part.total), [26, 18]);
assert.equal(roll.roll.total, 44);
load("browser-grid-geometry.js");
load("browser-grid-barriers.js");
load("browser-forced-movement.js");
window.IRON_PIT_BROWSER_STATE = { sizeAtMost: () => true };
window.IRON_PIT_BROWSER_CREATURE_KIND = { matches: () => false };
window.IRON_PIT_BROWSER_ON_HIT_CONDITION_LIFECYCLE = { attachStartTurnDamage: () => {} };
window.IRON_PIT_BROWSER_SAVING_THROWS = {
  resolveSavingThrow: () => ({ roll: { total: 1 }, succeeded: false }),
};
load("browser-on-hit-condition-save.js");
const member = (id, side, x) => ({
  combatant_id: id, side, state: {
    template: { id, name: id, size: "medium" },
    position: { x, y: 1 }, active_effect_ids: [],
    is_alive: true, is_dead: false,
  },
});
const attacker = member("attacker", "monsters", 1);
const target = member("target", "heroes", 6);
const setup = {
  heroes: [target], monsters: [attacker],
  map_definition: { width_squares: 10, height_squares: 4, cell_size_ft: 5 },
  persistent_barriers: [],
};
const effect = {
  onHitConditionSave: {
    saveAbility: "strength", dc: 20, conditionId: null, failurePullFt: 25,
  },
};
const moved = window.IRON_PIT_BROWSER_ON_HIT_CONDITION_SAVE.resolve(
  target, effect, attacker.state.template, 1, setup, attacker,
);
assert.equal(moved.saveSucceeded, false);
assert.equal(moved.saveDc, 20);
assert.equal(moved.forcedMovementFt, 20);
assert.equal(moved.forcedMovementDirection, "toward_source");
assert.deepEqual(target.state.position, { x: 2, y: 1 });
assert.deepEqual(target.state.active_effect_ids, []);
window.IRON_PIT_BROWSER_SAVING_THROWS.resolveSavingThrow =
  () => ({ roll: { total: 20 }, succeeded: true });
const succeedingTarget = member("success", "heroes", 6);
setup.heroes = [succeedingTarget];
const saved = window.IRON_PIT_BROWSER_ON_HIT_CONDITION_SAVE.resolve(
  succeedingTarget, effect, attacker.state.template, 1, setup, attacker,
);
assert.equal(saved.saveSucceeded, true);
assert.equal(saved.forcedMovementFt, 0);
assert.deepEqual(succeedingTarget.state.position, { x: 6, y: 1 });
console.log("2014 Balor universal triple critical and save pull parity passed.");
