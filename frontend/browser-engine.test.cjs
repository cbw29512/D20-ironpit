"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;

const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters.js", "browser-state.js", "browser-rage.js", "browser-rolls.js",
  "browser-attack.js", "browser-charge.js", "browser-multiattack.js", "browser-turn.js", "browser-engine.js",
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
  const battle = fight(["karnok-stoneward-l1"], ["srd-black-bear"], 5, queuedDice([1, 20, 15, 1, 15, 1]));
  const strikes = battle.events.filter((event) => event.round_number === 1 && event.event_type === "attack" && event.actor_id.startsWith("monster-1:"));
  assert.equal(strikes.length, 2, "Black Bear should make two Rend attacks");
  assert.deepEqual(strikes.map((event) => event.weapon_id), ["black-bear-rend", "black-bear-rend"]);
}

{
  const battle = fight(["karnok-stoneward-l1"], ["srd-brown-bear"], 5, queuedDice([1, 20, 15, 1, 15, 1]));
  const strikes = battle.events.filter((event) => event.round_number === 1 && event.event_type === "attack" && event.actor_id.startsWith("monster-1:"));
  assert.deepEqual(strikes.map((event) => event.weapon_id), ["brown-bear-bite", "brown-bear-claw"]);
  assert.ok(strikes[1].applied_condition_ids?.includes("prone"), "Brown Bear Claw should knock a surviving Large-or-smaller target Prone");
}

{
  const heroTemplate = structuredClone(window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"]);
  const boarTemplate = structuredClone(window.IRON_PIT_BROWSER_MONSTERS["srd-boar"]);
  const hero = { combatant_id: "hero-1:karnok", side: "heroes", position_ft: 0, state: window.IRON_PIT_BROWSER_STATE.buildState(heroTemplate) };
  const boar = { combatant_id: "monster-1:boar", side: "monsters", position_ft: 30, state: window.IRON_PIT_BROWSER_STATE.buildState(boarTemplate) };
  window.IRON_PIT_BROWSER_STATE.beginTurn(boar.state);
  window.IRON_PIT_DICE = queuedDice([15, 2, 3]);
  const charged = window.IRON_PIT_BROWSER_CHARGE.resolveClosing(1, 1, boar, hero);
  assert.equal(charged.handled, true);
  assert.equal(charged.events[0].movement_ft, 25);
  assert.equal(charged.events[1].feature_id, "charge");
  assert.equal(charged.events[1].damage_roll.notation, "1d6+1 + 1d6+0");
  assert.ok(charged.events[1].applied_condition_ids.includes("prone"));
}

{
  const heroTemplate = structuredClone(window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"]);
  const boarTemplate = structuredClone(window.IRON_PIT_BROWSER_MONSTERS["srd-boar"]);
  const hero = { combatant_id: "hero-1:karnok", side: "heroes", position_ft: 0, state: window.IRON_PIT_BROWSER_STATE.buildState(heroTemplate) };
  const boar = { combatant_id: "monster-1:boar", side: "monsters", position_ft: 5, state: window.IRON_PIT_BROWSER_STATE.buildState(boarTemplate) };
  boar.state.current_hp = 6;
  window.IRON_PIT_DICE = queuedDice([4, 15, 3]);
  const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(1, 1, boar, hero, boarTemplate.attacks[0], 5);
  assert.equal(event.attack_roll.mode, "advantage");
  assert.equal(event.attack_roll.selected_roll, 15);
}

{
  const battle = fight(["rokhan-stonefury-l1"], ["srd-commoner"], 5, queuedDice([20, 1, 15, 6, 6]));
  const rage = battle.events.find((event) => event.actor_id.startsWith("hero-1:") && event.feature_id === "rage");
  const attack = battle.events.find((event) => event.actor_id.startsWith("hero-1:") && event.event_type === "attack");
  assert.ok(rage, "audited Barbarian should Rage in combat");
  assert.equal(attack?.weapon_id, "rokhan-greataxe");
  assert.equal(attack?.damage_roll?.modifier, 5, "Rokhan should add +3 Strength and +2 Rage damage");
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
