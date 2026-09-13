"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;

const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters-generated.js",
  "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-resources.js", "browser-recharge.js", "browser-grapple.js", "browser-timed-conditions.js",
  "browser-weapon-mastery.js", "browser-state.js", "browser-rage.js", "browser-rolls.js", "browser-zero-hp.js",
  "browser-graze.js", "browser-vex.js", "browser-attack.js", "browser-reactions.js",
  "browser-dodge.js", "browser-saves.js", "browser-condition-lifecycle.js", "browser-charge.js",
  "browser-light-weapons.js", "browser-light-attack.js", "browser-standard-attack-action.js",
  "browser-multiattack.js", "browser-healing.js", "browser-spellcasting.js", "browser-condition-removal.js",
  "browser-support.js", "browser-formation.js", "browser-recharge-action.js", "browser-arena-map.js",
  "browser-grid-geometry.js", "browser-grid-movement-support.js", "browser-grid-path-search-support.js",
  "browser-grid-path-search.js", "browser-grid-movement.js", "browser-grid-reaction-support.js",
  "browser-reaction-movement.js", "browser-offensive-ranges.js", "browser-offensive-movement.js",
  "browser-grid-placement.js", "browser-progression-recovery.js", "browser-turn.js", "browser-initiative.js", "browser-engine.js",
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

function fight(heroIds, monsterIds, dice = deterministicDice()) {
  window.IRON_PIT_DICE = dice;
  return window.IRON_PIT_BROWSER_ENGINE.runEncounter({ hero_ids: heroIds, monster_ids: monsterIds });
}

function assertBattleShape(result) {
  assert.ok(result);
  assert.ok(["heroes_win", "monsters_win", "draw"].includes(result.outcome));
  assert.ok(Number.isInteger(result.rounds_completed));
  assert.ok(Array.isArray(result.events));
  assert.ok(result.events.length > 0);
  assert.ok(result.setup);
}

{
  const battle = fight(["karnok-stoneward-l1"], ["srd-commoner"]);
  assertBattleShape(battle);
}

{
  const battle = fight(["karnok-stoneward-l1"], ["srd-scout"]);
  assertBattleShape(battle);
}

{
  const battle = fight(["karnok-stoneward-l1"], ["srd-ogre"]);
  assertBattleShape(battle);
}

{
  const first = fight(["karnok-stoneward-l1"], ["srd-commoner"], deterministicDice(17));
  const second = fight(["karnok-stoneward-l1"], ["srd-commoner"], deterministicDice(17));
  assert.deepEqual(first.events, second.events, "same dice stream must produce the same audit-grade event log");
}

{
  const battle = fight(["karnok-stoneward-l1"], ["srd-ogre"], queuedDice([10, 10, 10, 10], 10));
  assertBattleShape(battle);
}

console.log("Browser encounter engine regressions passed.");