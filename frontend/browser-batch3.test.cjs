"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters.js", "browser-monsters-fixed.js",
  "browser-monsters-beast2.js", "browser-monsters-batch3.js", "browser-state.js",
  "browser-rage.js", "browser-rolls.js", "browser-attack.js", "browser-charge.js",
  "browser-multiattack.js", "browser-turn.js", "browser-engine.js",
]) load(file);

function queuedDice(values, fallback = 10) {
  const queue = [...values];
  const roll = (sides) => ((queue.length ? queue.shift() : fallback) - 1) % sides + 1;
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
}

const S = window.IRON_PIT_BROWSER_STATE;
const M = window.IRON_PIT_BROWSER_MULTIATTACK;
const monsters = window.IRON_PIT_BROWSER_MONSTERS;
const heroes = window.IRON_PIT_BROWSER_HEROES;

assert.equal(Object.keys(monsters).length, 55, "browser runtime should expose exactly 55 certified candidates");

function freshHero() {
  return {
    combatant_id: "hero-1:karnok", side: "heroes", position_ft: 0,
    state: S.buildState(structuredClone(heroes["karnok-stoneward-l1"])),
  };
}

function multiattackIds(monsterId, distance) {
  const attacker = {
    combatant_id: `monster-1:${monsterId}`, side: "monsters", position_ft: distance,
    state: S.buildState(structuredClone(monsters[monsterId])),
  };
  const hero = freshHero();
  const setup = { heroes: [hero], monsters: [attacker], starting_distance_ft: distance };
  S.beginTurn(attacker.state);
  window.IRON_PIT_DICE = queuedDice([10, 1, 1, 10, 1, 1]);
  return M.resolveAttackAction(1, 1, attacker, setup).events
    .filter((event) => event.event_type === "attack")
    .map((event) => event.weapon_id);
}

assert.deepEqual(multiattackIds("srd-owlbear", 5), ["owlbear-rend", "owlbear-rend"]);
assert.deepEqual(multiattackIds("srd-saber-toothed-tiger", 5), [
  "saber-toothed-tiger-rend", "saber-toothed-tiger-rend",
]);
assert.deepEqual(multiattackIds("srd-scout", 30), ["scout-longbow", "scout-longbow"]);
assert.deepEqual(multiattackIds("srd-scout", 5), ["scout-shortsword", "scout-shortsword"]);

{
  const ogre = monsters["srd-ogre"];
  assert.equal(ogre.attacks[0].id, "ogre-greatclub");
  assert.deepEqual([ogre.attacks[0].bonus, ogre.attacks[0].diceCount, ogre.attacks[0].diceSize, ogre.attacks[0].damageBonus], [6, 2, 8, 4]);
  assert.deepEqual([ogre.attacks[1].normal, ogre.attacks[1].long], [30, 120]);
}

{
  const one = {
    combatant_id: "monster-1:infantry", side: "monsters", position_ft: 5,
    state: S.buildState(structuredClone(monsters["srd-warrior-infantry"])),
  };
  const two = {
    combatant_id: "monster-2:infantry", side: "monsters", position_ft: 5,
    state: S.buildState(structuredClone(monsters["srd-warrior-infantry"])),
  };
  assert.equal(S.packTactics(one, { heroes: [freshHero()], monsters: [one, two] }), true);
  assert.deepEqual([one.state.template.attacks[1].normal, one.state.template.attacks[1].long], [20, 60]);
}

console.log("55-monster browser batch regressions passed.");
