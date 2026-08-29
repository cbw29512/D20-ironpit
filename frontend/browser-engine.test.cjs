"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;

const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters.js", "browser-state.js", "browser-rolls.js",
  "browser-attack.js", "browser-turn.js", "browser-engine.js",
]) load(file);

function deterministicDice(seed = 12345) {
  let state = seed >>> 0;
  const roll = (sides) => {
    state = (1664525 * state + 1013904223) >>> 0;
    return (state % sides) + 1;
  };
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
}

function queuedDice(values, fallback = 10) {
  const queue = [...values];
  const roll = (sides) => {
    const raw = queue.length ? queue.shift() : fallback;
    return ((raw - 1) % sides) + 1;
  };
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
}

function fight(heroIds, monsterIds, distance = 30, dice = deterministicDice()) {
  window.IRON_PIT_DICE = dice;
  return window.IRON_PIT_BROWSER_ENGINE.runEncounter({ hero_ids: heroIds, monster_ids: monsterIds, starting_distance_ft: distance });
}

{
  const battle = fight(["karnok-stoneward-l1"], ["srd-commoner"]);
  assert.notEqual(battle.outcome, "active");
  assert.ok(battle.events.some((event) => event.event_type === "attack"));
}

{
  const battle = fight(["karnok-stoneward-l1"], ["srd-bandit"], 30, deterministicDice(7));
  const karnokAttacks = battle.events.filter((event) => event.event_type === "attack" && event.actor_id.startsWith("hero-1:"));
  assert.equal(karnokAttacks[0].weapon_id, "karnok-shortbow");
  assert.equal(karnokAttacks.filter((event) => event.weapon_id === "karnok-shortbow").length, 1);
}

{
  const battle = fight(["karnok-stoneward-l1"], ["srd-dire-wolf", "srd-dire-wolf"], 5, queuedDice([1, 20, 20, 20, 10, 10, 10]));
  const packAttack = battle.events.find((event) => event.event_type === "attack" && event.feature_id === "pack-tactics");
  assert.ok(packAttack, "expected Pack Tactics attack");
  assert.equal(packAttack.attack_roll.mode, "advantage");
}

{
  const battle = fight(["karnok-stoneward-l1"], ["srd-dire-wolf"], 5,
    queuedDice([20, 1, 20, 1, 1, 1, 1, 1, 1, 1, 1, 10, 1]));
  assert.ok(battle.events.some((event) => event.event_type === "attack" && event.critical), "expected a critical attack");
  assert.ok(battle.events.some((event) => event.event_type === "attack" && event.attack_roll.selected_roll === 1), "expected a natural 1 attack");
}

{
  const battle = fight(["karnok-stoneward-l1"], ["srd-wolf", "srd-wolf"], 5,
    queuedDice([1, 20, 20, 20, 6, 6, 10, 10]));
  assert.ok(battle.events.some((event) => event.applied_condition_ids?.includes("prone")), "expected Wolf/Dire Wolf Prone support");
}

{
  const battle = fight(["karnok-stoneward-l1"], ["srd-axe-beak"], 90, deterministicDice(11));
  assert.ok(battle.events.some((event) => event.feature_id === "dodge" && event.actor_id.startsWith("monster-")), "expected melee-only monster to Dodge while closing");
}

{
  const heroes = Array(8).fill("karnok-stoneward-l1");
  const monsters = Array(8).fill("srd-wolf");
  const battle = fight(heroes, monsters, 30, deterministicDice(42));
  assert.notEqual(battle.outcome, "active");
  assert.ok(battle.rounds <= 100);
  assert.equal(battle.setup.heroes.length, 8);
  assert.equal(battle.setup.monsters.length, 8);
}

console.log("Browser combat regressions passed.");
