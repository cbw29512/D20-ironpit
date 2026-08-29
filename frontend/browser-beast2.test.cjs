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
const M = window.IRON_PIT_BROWSER_MULTIATTACK;
const monsters = window.IRON_PIT_BROWSER_MONSTERS;
const heroes = window.IRON_PIT_BROWSER_HEROES;

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

console.log("Second browser beast batch regressions passed.");
