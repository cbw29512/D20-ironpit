"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters.js", "browser-condition-immunity.js", "browser-condition-rules.js",
  "browser-action-economy.js", "browser-grapple.js", "browser-state.js", "browser-rolls.js", "browser-zero-hp.js",
  "browser-attack.js", "browser-formation.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const A = window.IRON_PIT_BROWSER_ATTACK;
const F = window.IRON_PIT_BROWSER_FORMATION;
const G = window.IRON_PIT_BROWSER_GRAPPLE;
const heroes = window.IRON_PIT_BROWSER_HEROES;
const monsters = window.IRON_PIT_BROWSER_MONSTERS;
const member = (id, side, template, position = side === "heroes" ? 0 : 5) => ({
  combatant_id: id, side, position_ft: position, state: S.buildState(structuredClone(template)),
});
const queuedDice = (values, fallback = 10) => {
  const queue = [...values];
  const roll = (sides) => ((queue.length ? queue.shift() : fallback) - 1) % sides + 1;
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
};

const attacker = member("monster-1:crab", "monsters", monsters["srd-giant-crab"]);
const held = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"], 0);
const other = member("hero-2:rokhan", "heroes", heroes["rokhan-stonefury-l1"], 0);
const base = attacker.state.template.attacks[0];
const tail = {
  ...base, id: "tail", name: "Tail", bonus: -20, kind: "melee", reach: 10,
  diceCount: 1, diceSize: 6, damageBonus: 0, damageType: "bludgeoning",
  controlEffect: null, forbidSelfGrappledTarget: false, grappleTargetPolicy: "auto_hit_own_grapple",
};
attacker.state.template.attacks = [tail];
held.state.template.armor_class = 99;
G.apply(held.state, attacker.combatant_id, 12, 10, false, tail.id);

const choice = F.chooseAttack(attacker, { heroes: [other, held], monsters: [attacker] }, [tail.id], "melee");
assert.equal(choice.target, held, "the held target must remain the only legal Tail target");

window.IRON_PIT_DICE = queuedDice([4]);
const event = A.resolveAttack(1, 1, attacker, held, tail, 5);
assert.equal(event.hit, true);
assert.equal(event.attack_roll, null);
assert.equal(event.critical, false);
assert.equal(event.damage_roll.total, 4, "the first die must be damage because no d20 is rolled");
assert.match(event.description, /Automatic hit: no attack roll/);

console.log("Browser grapple-locked automatic attack regression passed.");
