"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters.js", "browser-monsters-fixed.js", "browser-monsters-beast2.js",
  "browser-state.js", "browser-rage.js", "browser-rolls.js", "browser-attack.js",
  "browser-charge.js", "browser-multiattack.js", "browser-turn.js", "browser-engine.js",
]) load(file);

function queuedDice(values, fallback = 10) {
  const queue = [...values];
  const roll = (sides) => ((queue.length ? queue.shift() : fallback) - 1) % sides + 1;
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
}

const S = window.IRON_PIT_BROWSER_STATE;
const A = window.IRON_PIT_BROWSER_ATTACK;
const C = window.IRON_PIT_BROWSER_CHARGE;
const M = window.IRON_PIT_BROWSER_MULTIATTACK;
const monsters = window.IRON_PIT_BROWSER_MONSTERS;
const heroes = window.IRON_PIT_BROWSER_HEROES;

assert.equal(Object.keys(monsters).length, 45, "browser runtime should expose exactly 45 certified monsters");

{
  const tiger = { combatant_id: "monster-1:tiger", side: "monsters", position_ft: 5, state: S.buildState(structuredClone(monsters["srd-tiger"])) };
  const hero = { combatant_id: "hero-1:karnok", side: "heroes", position_ft: 0, state: S.buildState(structuredClone(heroes["karnok-stoneward-l1"])) };
  S.beginTurn(tiger.state);
  window.IRON_PIT_DICE = queuedDice([15, 1, 1]);
  const event = A.resolveAttack(1, 1, tiger, hero, tiger.state.template.attacks[0], 5);
  assert.equal(event.hit, true);
  assert.ok(event.applied_condition_ids.includes("prone"), "Tiger Rend should knock a surviving Large-or-smaller target Prone");
}

{
  const bear = { combatant_id: "monster-1:polar", side: "monsters", position_ft: 5, state: S.buildState(structuredClone(monsters["srd-polar-bear"])) };
  const hero = { combatant_id: "hero-1:karnok", side: "heroes", position_ft: 0, state: S.buildState(structuredClone(heroes["karnok-stoneward-l1"])) };
  const setup = { heroes: [hero], monsters: [bear], starting_distance_ft: 5 };
  S.beginTurn(bear.state);
  window.IRON_PIT_DICE = queuedDice([15, 1, 15, 1]);
  const result = M.resolveAttackAction(1, 1, bear, setup);
  const attacks = result.events.filter((event) => event.event_type === "attack");
  assert.equal(attacks.length, 2, "Polar Bear should make two Rend attacks");
  assert.deepEqual(attacks.map((event) => event.weapon_id), ["polar-bear-rend", "polar-bear-rend"]);
}

{
  const one = { combatant_id: "monster-1:vulture", side: "monsters", position_ft: 5, state: S.buildState(structuredClone(monsters["srd-vulture"])) };
  const two = { combatant_id: "monster-2:vulture", side: "monsters", position_ft: 5, state: S.buildState(structuredClone(monsters["srd-vulture"])) };
  const hero = { combatant_id: "hero-1:karnok", side: "heroes", position_ft: 0, state: S.buildState(structuredClone(heroes["karnok-stoneward-l1"])) };
  assert.equal(S.packTactics(one, { heroes: [hero], monsters: [one, two] }), true);
}

{
  const beetle = { combatant_id: "monster-1:beetle", side: "monsters", position_ft: 5, state: S.buildState(structuredClone(monsters["srd-giant-fire-beetle"])) };
  const hero = { combatant_id: "hero-1:karnok", side: "heroes", position_ft: 0, state: S.buildState(structuredClone(heroes["karnok-stoneward-l1"])) };
  S.beginTurn(beetle.state);
  window.IRON_PIT_DICE = queuedDice([20]);
  const event = A.resolveAttack(1, 1, beetle, hero, beetle.state.template.attacks[0], 5);
  assert.equal(event.critical, true);
  assert.equal(event.damage_roll.total, 1, "Giant Fire Beetle flat fire damage must stay 1 on a critical hit");
  assert.deepEqual(beetle.state.template.damage_resistances, ["fire"]);
}

{
  const goat = { combatant_id: "monster-1:goat", side: "monsters", position_ft: 30, state: S.buildState(structuredClone(monsters["srd-giant-goat"])) };
  const hero = { combatant_id: "hero-1:karnok", side: "heroes", position_ft: 0, state: S.buildState(structuredClone(heroes["karnok-stoneward-l1"])) };
  S.beginTurn(goat.state);
  window.IRON_PIT_DICE = queuedDice([15, 2, 3, 4]);
  const charged = C.resolveClosing(1, 1, goat, hero);
  assert.equal(charged.handled, true);
  assert.equal(charged.events[0].movement_ft, 25);
  assert.equal(charged.events[1].feature_id, "charge");
  assert.equal(charged.events[1].damage_roll.notation, "1d6+3 + 2d4+0");
  assert.ok(charged.events[1].applied_condition_ids.includes("prone"));
}

{
  const owl = monsters["srd-giant-owl"];
  assert.equal(owl.attacks[0].diceSize, 10);
  assert.deepEqual(owl.damage_resistances, ["necrotic", "radiant"]);
}

{
  const one = { combatant_id: "monster-1:hyena", side: "monsters", position_ft: 5, state: S.buildState(structuredClone(monsters["srd-hyena"])) };
  const two = { combatant_id: "monster-2:hyena", side: "monsters", position_ft: 5, state: S.buildState(structuredClone(monsters["srd-hyena"])) };
  const hero = { combatant_id: "hero-1:karnok", side: "heroes", position_ft: 0, state: S.buildState(structuredClone(heroes["karnok-stoneward-l1"])) };
  assert.equal(S.packTactics(one, { heroes: [hero], monsters: [one, two] }), true);
}

console.log("Expanded browser beast batch regressions passed.");
