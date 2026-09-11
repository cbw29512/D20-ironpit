"use strict";
// Real generated monster data enters the same turn resolver used by the live engine.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js",
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
  "browser-grid-placement.js", "browser-turn.js", "browser-initiative.js", "browser-engine.js",
]) load(file);

for (const file of ["browser-monsters-generated.js", "browser-area-shapes.js",
  "browser-area-targeting.js", "browser-save-targets.js", "browser-offense-value.js"]) load(file);

function fixture(id, x) {
  try {
    const member = (template, side, position) => ({
      combatant_id: `${side}:${template.id}`, side,
      state: window.IRON_PIT_BROWSER_STATE.buildState(structuredClone(template)),
    });
    const hero = member(window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"], "heroes");
    const monster = member(window.IRON_PIT_BROWSER_MONSTERS[id], "monsters");
    hero.state.position = { x: 0, y: 6 };
    monster.state.position = { x, y: 6 };
    hero.state.initiative_total = 10;
    monster.state.initiative_total = 20;
    return { hero, monster, setup: { heroes: [hero], monsters: [monster],
      map_definition: window.IRON_PIT_BROWSER_ARENA_MAP.buildStandardMap() } };
  } catch (error) {
    console.error("Failed source monster Recharge fixture", { id, error });
    throw error;
  }
}

function turn(fight, round, values) {
  try {
    const queue = [...values];
    const roll = (sides) => {
      const value = queue.shift();
      assert.ok(value >= 1 && value <= sides, `Unexpected d${sides} roll: ${value}`);
      return value;
    };
    window.IRON_PIT_DICE = { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
    const result = window.IRON_PIT_BROWSER_TURN.resolveTurn(1, round, fight.monster, fight.setup);
    assert.equal(queue.length, 0, "Every expected die must be consumed exactly once");
    return result.events;
  } catch (error) {
    console.error("Failed source monster Recharge turn", { round, error });
    throw error;
  }
}

for (const example of [
  { id: "srd-ape", x: 5, resource: "ape-rock-recharge", first: [15, 1, 1],
    fallback: [5, 10, 10], attack: "ape-fist" },
  { id: "srd-hell-hound", x: 1, resource: "hell-hound-fire-breath-recharge", first: [20, 1, 1, 1, 1, 1],
    fallback: [4, 19, 1, 1, 19, 1, 1], attack: "hell-hound-bite" },
]) {
  const original = JSON.stringify(window.IRON_PIT_BROWSER_MONSTERS[example.id]);
  const fight = fixture(example.id, example.x);
  assert.equal(fight.monster.state.resources[example.resource], 1);
  const first = turn(fight, 1, example.first);
  assert.equal(first.filter((event) => event.resource_roll).length, 0);
  const offense = first.filter((event) => ["attack", "saving_throw"].includes(event.event_type));
  assert.equal(offense.length, 1, "Recharge ability spends the action instead of adding to Multiattack");
  assert.equal(offense[0].weapon_id || offense[0].feature_id,
    example.id === "srd-ape" ? "ape-rock" : "hell-hound-fire-breath");
  assert.equal(fight.monster.state.resources[example.resource], 0);
  const second = turn(fight, 2, example.fallback);
  assert.equal(second.filter((event) => event.resource_roll).length, 1);
  assert.deepEqual(second.filter((event) => event.event_type === "attack").map((event) => event.weapon_id),
    [example.attack, example.attack]);
  assert.equal(fight.monster.state.resources[example.resource], 0);
  assert.equal(fixture(example.id, example.x).monster.state.resources[example.resource], 1);
  assert.equal(JSON.stringify(window.IRON_PIT_BROWSER_MONSTERS[example.id]), original,
    "Fight mutations must never change generated source templates");
}
console.log("Source-bound Ape and Hell Hound browser Recharge regressions passed.");