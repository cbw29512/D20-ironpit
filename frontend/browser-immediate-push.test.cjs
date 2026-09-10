"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters.js", "browser-state.js", "browser-rage.js",
  "browser-rolls.js", "browser-zero-hp.js", "browser-attack.js", "browser-charge.js",
  "browser-formation.js", "browser-standard-attack-action.js", "browser-multiattack.js",
]) load(file);

function queuedDice(values, fallback = 10) {
  const queue = [...values];
  const roll = (sides) => ((queue.length ? queue.shift() : fallback) - 1) % sides + 1;
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
}

function fight(firstRoll) {
  const S = window.IRON_PIT_BROWSER_STATE;
  const template = structuredClone(window.IRON_PIT_BROWSER_MONSTERS["srd-bandit"]);
  const melee = template.attacks.find((attack) => attack.id === "bandit-scimitar");
  melee.pushTargetAwayFt = 10;
  template.attack_action = {
    id: "push-then-shoot", name: "Push then Shoot",
    slots: [
      { attackIds: ["bandit-scimitar"], saveActionIds: [] },
      { attackIds: ["bandit-light-crossbow"], saveActionIds: [] },
    ],
  };
  const attacker = { combatant_id: "monster-1:bandit", side: "monsters", position_ft: 20, state: S.buildState(template) };
  const target = {
    combatant_id: "hero-1:karnok", side: "heroes", position_ft: 15,
    state: S.buildState(structuredClone(window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"])),
  };
  S.beginTurn(attacker.state);
  window.IRON_PIT_DICE = queuedDice([firstRoll, 1, 10, 10, 1]);
  return { attacker, target, attacks: window.IRON_PIT_BROWSER_MULTIATTACK.resolveAttackAction(1, 1, attacker, { heroes: [target], monsters: [attacker] }).events.filter((event) => event.event_type === "attack") };
}

{
  const result = fight(15);
  assert.equal(result.attacks[0].hit, true);
  assert.equal(result.target.position_ft, 5);
  assert.equal(result.attacks[0].distance_before_ft, 5);
  assert.equal(result.attacks[0].distance_after_ft, 15);
  assert.equal(result.attacks[1].attack_roll.mode, "normal");
}

{
  const result = fight(1);
  assert.equal(result.attacks[0].hit, false);
  assert.equal(result.target.position_ft, 15);
  assert.equal(result.attacks[1].attack_roll.mode, "disadvantage");
}

console.log("browser immediate push parity passed.");
