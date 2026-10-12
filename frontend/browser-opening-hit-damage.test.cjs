"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (file) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, file), "utf8"), { filename: file },
);
window.IRON_PIT_DICE = {
  queue: [],
  roll(sides) {
    const value = this.queue.shift();
    if (!Number.isInteger(value) || value < 1 || value > sides) throw new Error("Bad deterministic roll");
    return value;
  },
  rollMany(count, sides) { return Array.from({ length: count }, () => this.roll(sides)); },
};
load("browser-timed-control-limits.js");
load("browser-rolls.js");

const register = window.IRON_PIT_BROWSER_TIMED_CONTROL.registerTurnAttack;
const damage = window.IRON_PIT_BROWSER_ROLLS.weaponDamage;
const weapon = {
  name: "Morningstar", kind: "melee", diceCount: 2, diceSize: 8,
  damageBonus: 2, damageType: "piercing", onHitDamage: [],
  conditionalDamage: {
    trigger: "round1_initiative_lead", mode: "add", diceCount: 2, diceSize: 6,
    damageBonus: 0, damageType: "piercing", sourceName: "Surprise Attack",
  },
};
const attacker = () => ({
  template: { max_hp: 20, traits: [] },
  current_hp: 20, turns_started: 1, attacks_this_turn: 0,
  feature_last_turn_keys: {}, feature_use_counts: {},
});
const target = () => ({ current_hp: 20, turns_started: 0, template: { max_hp: 20 } });
const hit = (a, t, rolls, critical = false) => {
  window.IRON_PIT_DICE.queue = [...rolls];
  const result = damage(a, weapon, critical, "normal", "1:bugbear", null, t);
  assert.deepEqual(window.IRON_PIT_DICE.queue, []);
  return result.components;
};

// Winning initiative, first attack and one conditional rider — never double it.
{
  const a = attacker(), t = target();
  register(a);
  const components = hit(a, t, [2, 3, 4, 5]);
  assert.deepEqual(components.map((part) => part.source), ["Morningstar", "Surprise Attack"]);
  assert.deepEqual(components[1].rolls, [4, 5]);
  assert.equal(components[1].damage_type, "piercing");
}
// Missed first attempt still consumed; second attack has no opening bonus.
{
  const a = attacker(), t = target();
  register(a); // First attack missed, so no damage roll.
  register(a);
  assert.deepEqual(hit(a, t, [2, 3]).map((part) => part.source), ["Morningstar"]);
}
// Target already went first, or attacker did not attack on their first turn.
for (const [own, theirs] of [[1, 1], [2, 0]]) {
  const a = attacker(), t = target();
  a.turns_started = own; t.turns_started = theirs;
  register(a);
  assert.deepEqual(hit(a, t, [2, 3]).map((part) => part.source), ["Morningstar"]);
}
// A critical doubles the 2d8 weapon dice and 2d6 bonus dice exactly once.
{
  const a = attacker(), t = target();
  register(a);
  const components = hit(a, t, [2, 3, 4, 5, 1, 2, 3, 4], true);
  assert.deepEqual(components[1].rolls, [1, 2, 3, 4]);
}
// An off-turn attempt consumes first-attack entitlement, too.
{
  const a = attacker(), t = target();
  register(a, true);
  register(a);
  assert.deepEqual(hit(a, t, [2, 3]).map((part) => part.source), ["Morningstar"]);
}
{
  const a = attacker(), t = target();
  assert.deepEqual(a.feature_use_counts, {});
  register(a);
  assert.equal(hit(a, t, [2, 3, 4, 5]).length, 2);
}
console.log("2014 opening-initiative source conditional damage browser regressions passed.");
