"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters.js", "browser-grapple.js", "browser-timed-conditions.js",
  "browser-state.js", "browser-rage.js", "browser-rolls.js", "browser-zero-hp.js", "browser-attack.js",
]) load(file);

const queuedDice = (values, fallback = 10) => {
  const queue = [...values];
  const roll = (sides) => ((queue.length ? queue.shift() : fallback) - 1) % sides + 1;
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
};
const S = window.IRON_PIT_BROWSER_STATE;
const A = window.IRON_PIT_BROWSER_ATTACK;
const heroes = window.IRON_PIT_BROWSER_HEROES;
const monsters = window.IRON_PIT_BROWSER_MONSTERS;
const member = (id, side, template, position = side === "heroes" ? 0 : 5) => ({
  combatant_id: id, side, position_ft: position, state: S.buildState(structuredClone(template)),
});
const venomBite = {
  id: "test-venom-bite", name: "Bite", kind: "melee", bonus: 6,
  diceCount: 1, diceSize: 4, damageBonus: 4, damageType: "piercing", reach: 5,
  animation: "bite", onHitDamage: [{ source: "Venom", diceCount: 1, diceSize: 8, damageBonus: 0, damageType: "poison" }],
};

{
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
  const commoner = member("monster-1:commoner", "monsters", monsters["srd-commoner"]);
  window.IRON_PIT_DICE = queuedDice([15, 3, 5]);
  const event = A.resolveAttack(1, 1, commoner, hero, venomBite, 5);
  assert.equal(event.hit, true); assert.equal(event.critical, false);
  assert.deepEqual(event.damage_components.map((part) => part.damage_type), ["piercing", "poison"]);
  assert.deepEqual(event.damage_components.map((part) => part.total), [7, 5]);
  assert.equal(event.damage_roll.total, 12);
}

{
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
  const commoner = member("monster-1:commoner", "monsters", monsters["srd-commoner"]);
  window.IRON_PIT_DICE = queuedDice([20, 2, 3, 4, 5]);
  const event = A.resolveAttack(1, 1, commoner, hero, venomBite, 5);
  assert.equal(event.critical, true);
  assert.deepEqual(event.damage_components.map((part) => part.notation), ["2d4+4", "2d8+0"]);
  assert.deepEqual(event.damage_components.map((part) => part.total), [9, 9]);
  assert.equal(event.damage_roll.total, 18);
}

{
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
  const commoner = member("monster-1:commoner", "monsters", monsters["srd-commoner"]);
  hero.state.template.damage_resistances = ["piercing"];
  hero.state.template.damage_immunities = ["poison"];
  window.IRON_PIT_DICE = queuedDice([15, 4, 8]);
  const event = A.resolveAttack(1, 1, commoner, hero, venomBite, 5);
  assert.deepEqual(event.damage_components.map((part) => part.total), [8, 8]);
  assert.deepEqual(event.damage_components.map((part) => part.applied_total), [4, 0]);
  assert.equal(event.damage_roll.total, 4);
}

console.log("Browser mixed typed hit-damage regressions passed.");
