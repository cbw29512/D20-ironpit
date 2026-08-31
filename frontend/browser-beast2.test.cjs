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

assert.equal(Object.keys(monsters).length, 50, "browser runtime should expose exactly 50 certified monsters");

function freshHero() {
  return { combatant_id: "hero-1:karnok", side: "heroes", position_ft: 0, state: S.buildState(structuredClone(heroes["karnok-stoneward-l1"])) };
}
function openingSetup(attacker, hero, attackerInit = 20, heroInit = 10) {
  attacker.state.initiative_total = attackerInit; hero.state.initiative_total = heroInit;
  return { heroes: [hero], monsters: [attacker], starting_distance_ft: 30 };
}

{
  const tiger = { combatant_id: "monster-1:tiger", side: "monsters", position_ft: 5, state: S.buildState(structuredClone(monsters["srd-tiger"])) };
  const hero = freshHero();
  S.beginTurn(tiger.state);
  window.IRON_PIT_DICE = queuedDice([15, 1, 1]);
  const event = A.resolveAttack(1, 1, tiger, hero, tiger.state.template.attacks[0], 5);
  assert.equal(event.hit, true);
  assert.ok(event.applied_condition_ids.includes("prone"));
}

{
  const bear = { combatant_id: "monster-1:polar", side: "monsters", position_ft: 5, state: S.buildState(structuredClone(monsters["srd-polar-bear"])) };
  const hero = freshHero();
  const setup = { heroes: [hero], monsters: [bear], starting_distance_ft: 5 };
  S.beginTurn(bear.state);
  window.IRON_PIT_DICE = queuedDice([15, 1, 15, 1]);
  const attacks = M.resolveAttackAction(1, 1, bear, setup).events.filter((event) => event.event_type === "attack");
  assert.equal(attacks.length, 2);
  assert.deepEqual(attacks.map((event) => event.weapon_id), ["polar-bear-rend", "polar-bear-rend"]);
}

{
  const beetle = { combatant_id: "monster-1:beetle", side: "monsters", position_ft: 5, state: S.buildState(structuredClone(monsters["srd-giant-fire-beetle"])) };
  const hero = freshHero();
  S.beginTurn(beetle.state);
  window.IRON_PIT_DICE = queuedDice([20]);
  const event = A.resolveAttack(1, 1, beetle, hero, beetle.state.template.attacks[0], 5);
  assert.equal(event.critical, true);
  assert.equal(event.damage_roll.total, 1, "flat damage must not double on a critical hit");
}

{
  const goat = { combatant_id: "monster-1:goat", side: "monsters", position_ft: 30, state: S.buildState(structuredClone(monsters["srd-giant-goat"])) };
  const hero = freshHero(), setup = openingSetup(goat, hero);
  S.beginTurn(goat.state);
  window.IRON_PIT_DICE = queuedDice([15, 2, 3, 4]);
  const charged = C.resolveClosing(1, 1, goat, hero, setup);
  assert.equal(charged.handled, true);
  assert.equal(charged.events[1].damage_roll.notation, "1d6+3 + 2d4+0");
  assert.ok(charged.events[1].applied_condition_ids.includes("prone"));
}

{
  const goat = { combatant_id: "monster-1:goat-slot", side: "monsters", position_ft: 5, state: S.buildState(structuredClone(monsters["srd-giant-goat"])) };
  const hero = freshHero(), setup = openingSetup(goat, hero);
  window.IRON_PIT_DICE = queuedDice([15, 2, 3, 4]);
  const turn = window.IRON_PIT_BROWSER_TURN.resolveTurn(1, 1, goat, setup);
  const attack = turn.events.find((event) => event.event_type === "attack");
  assert.equal(attack?.feature_id, "charge", "initiative sweep should assume pre-contact run-up from the melee slot");
  assert.equal(turn.events.some((event) => event.event_type === "movement"), false);
}

{
  const goat = { combatant_id: "monster-1:goat-loser", side: "monsters", position_ft: 30, state: S.buildState(structuredClone(monsters["srd-giant-goat"])) };
  const hero = freshHero(), setup = openingSetup(goat, hero, 10, 10);
  S.beginTurn(goat.state);
  assert.equal(C.resolveClosing(1, 1, goat, hero, setup).handled, false, "initiative tie must suppress the opener");
  assert.equal(C.resolveClosing(1, 2, goat, hero, openingSetup(goat, hero, 20, 10)).handled, false, "charge is opener-only");
}

{
  const mastiff = { combatant_id: "monster-1:mastiff", side: "monsters", position_ft: 5, state: S.buildState(structuredClone(monsters["srd-mastiff"])) };
  const hero = freshHero();
  S.beginTurn(mastiff.state);
  window.IRON_PIT_DICE = queuedDice([15, 1]);
  const event = A.resolveAttack(1, 1, mastiff, hero, mastiff.state.template.attacks[0], 5);
  assert.ok(event.applied_condition_ids.includes("prone"), "Mastiff Bite should knock Medium-or-smaller targets Prone");
}

for (const [id, notation] of [
  ["srd-rhinoceros", "2d8+5 + 2d8+0"],
  ["srd-warhorse", "2d4+4 + 2d4+0"],
]) {
  const attacker = { combatant_id: `monster-1:${id}`, side: "monsters", position_ft: 30, state: S.buildState(structuredClone(monsters[id])) };
  const hero = freshHero(), setup = openingSetup(attacker, hero);
  S.beginTurn(attacker.state);
  window.IRON_PIT_DICE = queuedDice([15, 1, 1, 1, 1]);
  const charged = C.resolveClosing(1, 1, attacker, hero, setup);
  assert.equal(charged.handled, true, `${id} should charge after an initiative sweep and 20+ foot close`);
  assert.equal(charged.events[0].movement_ft, 25);
  assert.equal(charged.events[1].damage_roll.notation, notation);
  assert.ok(charged.events[1].applied_condition_ids.includes("prone"));
}

assert.equal(monsters["srd-giant-bat"].speed_ft, 60);
assert.equal(monsters["srd-mule"].attacks[0].diceSize, 4);
assert.deepEqual(monsters["srd-giant-owl"].damage_resistances, ["necrotic", "radiant"]);

{
  const one = { combatant_id: "monster-1:hyena", side: "monsters", position_ft: 5, state: S.buildState(structuredClone(monsters["srd-hyena"])) };
  const two = { combatant_id: "monster-2:hyena", side: "monsters", position_ft: 5, state: S.buildState(structuredClone(monsters["srd-hyena"])) };
  assert.equal(S.packTactics(one, { heroes: [freshHero()], monsters: [one, two] }), true);
}

console.log("50-monster browser beast regressions passed.");
