"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters.js", "browser-grapple.js", "browser-timed-conditions.js",
  "browser-state.js", "browser-rage.js", "browser-rolls.js", "browser-zero-hp.js", "browser-ability-hooks.js", "browser-attack-outcome.js", "browser-attack.js", "browser-damage-defense-rules.js", "browser-hit-damage.js",
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
const ritualSickle = {
  id: "test-ritual-sickle", name: "Ritual Sickle", kind: "melee", bonus: 3,
  diceCount: 1, diceSize: 4, damageBonus: 1, damageType: "slashing", reach: 5,
  animation: "slash", onHitDamage: [{ source: "Necrotic", diceCount: 0, diceSize: 2, damageBonus: 1, damageType: "necrotic" }],
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
  window.IRON_PIT_DICE = queuedDice([20, 2, 3]);
  const event = A.resolveAttack(1, 1, commoner, hero, ritualSickle, 5);
  assert.equal(event.critical, true);
  assert.deepEqual(event.damage_components.map((part) => part.notation), ["2d4+1", "1"]);
  assert.deepEqual(event.damage_components.map((part) => part.total), [6, 1]);
  assert.equal(event.damage_roll.total, 7);
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


{
  // Names and IDs are card metadata, not branches in the damage resolver.
  const renamedSourceAttack = structuredClone(venomBite);
  renamedSourceAttack.id = "synthetic-anonymous-attack";
  renamedSourceAttack.name = "Completely Different Label";
  renamedSourceAttack.onHitDamage[0].source = "An Unrelated Effect Label";

  const check = (attack) => {
    const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
    const attacker = member("monster-1:commoner", "monsters", monsters["srd-commoner"]);
    hero.state.template.damage_resistances = ["piercing"];
    hero.state.template.damage_vulnerabilities = ["poison"];
    const startingHp = hero.state.current_hp;
    window.IRON_PIT_DICE = queuedDice([15, 4, 2]);
    const event = A.resolveAttack(1, 1, attacker, hero, attack, 5);
    assert.equal(event.hit, true);
    assert.deepEqual(event.damage_components.map((part) => part.damage_type), ["piercing", "poison"]);
    assert.deepEqual(event.damage_components.map((part) => part.total), [8, 2]);
    assert.deepEqual(event.damage_components.map((part) => part.applied_total), [4, 4]);
    assert.equal(event.damage_roll.total, 8);
    assert.equal(hero.state.current_hp, startingHp - 8);
    return event;
  };
  const original = check(venomBite);
  const renamed = check(renamedSourceAttack);
  assert.notEqual(original.attack_id, renamed.attack_id);
}

{
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
  const attacker = member("monster-1:commoner", "monsters", monsters["srd-commoner"]);
  const startingHp = hero.state.current_hp;
  window.IRON_PIT_DICE = queuedDice([1]);
  const event = A.resolveAttack(1, 1, attacker, hero, venomBite, 5);
  assert.equal(event.hit, false);
  assert.equal(event.turn_terminated, true); // Pit natural-1 policy.
  assert.deepEqual(event.damage_components, []);
  assert.equal(hero.state.current_hp, startingHp);
}


{
  // The mixed-type damage from one Bite shares a single hit/zero-HP event.
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
  const monster = member("monster-1:commoner", "monsters", monsters["srd-commoner"]);
  monster.state.current_hp = 5;
  window.IRON_PIT_DICE = queuedDice([15, 4, 2]);
  const event = A.resolveAttack(1, 1, hero, monster, venomBite, 5);
  assert.equal(event.hit, true);
  assert.deepEqual(event.damage_components.map((part) => part.damage_type), ["piercing", "poison"]);
  assert.deepEqual(event.damage_components.map((part) => part.applied_total), [8, 2]);
  assert.equal(event.damage_roll.total, 10);
  assert.equal(monster.state.current_hp, 0);
  assert.equal(monster.state.is_dead, true);
  assert.throws(() => A.resolveAttack(2, 1, hero, monster, venomBite, 5), /cannot be targeted/);
}

{
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
  const attacker = member("monster-1:commoner", "monsters", monsters["srd-commoner"]);
  hero.state.current_hp = 5;
  hero.state.resources["relentless-endurance"] = 0;
  window.IRON_PIT_DICE = queuedDice([15, 4, 2]);
  const event = A.resolveAttack(1, 1, attacker, hero, venomBite, 5);
  assert.deepEqual(event.damage_components.map((part) => part.applied_total), [8, 2]);
  assert.equal(hero.state.current_hp, 0);
  assert.equal(hero.state.is_unconscious, true);
  assert.equal(hero.state.is_dead, false);
  assert.equal(hero.state.death_save_failures, 0);
  // A *separate* later damaging event at 0 HP incurs a failed save.
  window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(hero.state, 2, false, ["poison"]);
  assert.equal(hero.state.death_save_failures, 1);
}

console.log("Browser mixed typed hit-damage regressions passed, including fixed typed riders.");
