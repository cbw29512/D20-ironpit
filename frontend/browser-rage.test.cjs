"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters.js", "browser-state.js", "browser-rage.js",
  "browser-rolls.js", "browser-attack.js", "browser-multiattack.js", "browser-turn.js", "browser-engine.js",
]) load(file);

function queuedDice(values, fallback = 10) {
  const queue = [...values];
  const roll = (sides) => ((queue.length ? queue.shift() : fallback) - 1) % sides + 1;
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
}

{
  window.IRON_PIT_DICE = queuedDice([20, 1, 15, 6, 6]);
  const battle = window.IRON_PIT_BROWSER_ENGINE.runEncounter({
    hero_ids: ["rokhan-stonefury-l1"], monster_ids: ["srd-commoner"], starting_distance_ft: 5,
  });
  const rage = battle.events.find((event) => event.feature_id === "rage");
  const attack = battle.events.find((event) => event.event_type === "attack" && event.actor_id.startsWith("hero-1:"));
  assert.ok(rage, "expected Rokhan to activate Rage before attacking");
  assert.ok(attack?.hit, "expected deterministic Rokhan hit");
  assert.equal(attack.weapon_id, "rokhan-greataxe");
  assert.equal(attack.damage_roll.modifier, 5, "expected +3 Strength and +2 Rage damage");
  assert.equal(attack.damage_roll.notation, "1d12+5");
}

{
  const barbarian = structuredClone(window.IRON_PIT_BROWSER_HEROES["rokhan-stonefury-l1"]);
  const bandit = structuredClone(window.IRON_PIT_BROWSER_MONSTERS["srd-bandit"]);
  const hero = { combatant_id: "hero-1:rokhan", side: "heroes", position_ft: 0, state: window.IRON_PIT_BROWSER_STATE.buildState(barbarian) };
  const monster = { combatant_id: "monster-1:bandit", side: "monsters", position_ft: 5, state: window.IRON_PIT_BROWSER_STATE.buildState(bandit) };
  window.IRON_PIT_BROWSER_STATE.beginTurn(hero.state);
  const rage = window.IRON_PIT_BROWSER_RAGE.enter(1, 1, hero);
  assert.ok(rage);
  window.IRON_PIT_DICE = queuedDice([15, 5]);
  const scimitar = bandit.attacks.find((item) => item.id === "bandit-scimitar");
  const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(2, 1, monster, hero, scimitar, 5);
  assert.equal(event.damage_components[0].total, 6);
  assert.equal(event.damage_components[0].applied_total, 3, "Rage should halve slashing damage");
  assert.equal(hero.state.current_hp, 11);
  hero.state.is_unconscious = true;
  window.IRON_PIT_BROWSER_RAGE.endIfIncapacitated(hero.state);
  assert.equal(window.IRON_PIT_BROWSER_RAGE.active(hero.state), false, "incapacitation should end Rage");
}

console.log("Browser Rage regressions passed.");
