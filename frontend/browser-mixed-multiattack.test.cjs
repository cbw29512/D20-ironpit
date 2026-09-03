"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters.js", "browser-monsters-fixed.js", "browser-monsters-beast2.js",
  "browser-monsters-batch3.js", "browser-monsters-control.js", "browser-monsters-poison.js", "browser-monsters-venom.js",
  "browser-monsters-mixed.js", "browser-condition-rules.js", "browser-action-economy.js", "browser-grapple.js",
  "browser-timed-conditions.js", "browser-state.js", "browser-rage.js", "browser-rolls.js", "browser-zero-hp.js",
  "browser-attack.js", "browser-saves.js", "browser-charge.js", "browser-formation.js", "browser-multiattack.js", "browser-turn.js",
]) load(file);

const queuedDice = (values, fallback = 10) => {
  const queue = [...values];
  const roll = (sides) => ((queue.length ? queue.shift() : fallback) - 1) % sides + 1;
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
};
const S = window.IRON_PIT_BROWSER_STATE;
const T = window.IRON_PIT_BROWSER_TURN;
const heroes = window.IRON_PIT_BROWSER_HEROES;
const monsters = window.IRON_PIT_BROWSER_MONSTERS;
const member = (id, side, template, position) => ({
  combatant_id: id, side, position_ft: position, state: S.buildState(structuredClone(template)),
});

assert.equal(Object.keys(monsters).length, 63, "mixed Multiattack batch must bring browser roster to 63 monsters");

{
  const snake = monsters["srd-giant-constrictor-snake"];
  assert.equal(snake.size, "huge");
  assert.equal(snake.armor_class, 12);
  assert.equal(snake.max_hp, 60);
  assert.deepEqual(snake.attack_action.slots, [
    { attackIds: ["giant-constrictor-snake-bite"], saveActionIds: [] },
    { attackIds: [], saveActionIds: ["giant-constrictor-snake-constrict"] },
  ]);
}

{
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"], 0);
  const snake = member("monster-1:giant-snake", "monsters", monsters["srd-giant-constrictor-snake"], 10);
  const setup = { heroes: [hero], monsters: [snake] };
  window.IRON_PIT_DICE = queuedDice([15, 1, 1, 1, 1, 1]);

  const result = T.resolveTurn(1, 1, snake, setup);
  const combat = result.events.filter((event) => event.event_type === "attack" || event.event_type === "saving_throw");

  assert.deepEqual(combat.map((event) => event.event_type), ["attack", "saving_throw"]);
  assert.equal(combat[0].weapon_id, "giant-constrictor-snake-bite");
  assert.equal(combat[1].feature_id, "giant-constrictor-snake-constrict");
  assert.equal(combat[1].save_succeeded, false);
  assert.deepEqual(combat[1].applied_condition_ids, ["grappled"]);
  assert.equal(snake.state.action_available, false);
  assert.equal(result.events.some((event) => event.event_type === "movement" || event.event_type === "dash"), false);
}

const hybrid = {
  id: "hybrid", name: "Hybrid", kind: "monster", size: "medium", armor_class: 12, max_hp: 30, speed_ft: 30,
  initiative_bonus: 0, primary_attack_id: "sword", traits: [], resources: {}, saving_throw_actions: [],
  attacks: [
    { id: "sword", name: "Sword", kind: "melee", bonus: 5, reach: 5, diceCount: 1, diceSize: 6, damageBonus: 3, damageType: "slashing" },
    { id: "bow", name: "Bow", kind: "ranged", bonus: 5, normal: 80, long: 320, diceCount: 1, diceSize: 6, damageBonus: 3, damageType: "piercing" },
  ],
  attack_action: { id: "hybrid-multiattack", name: "Multiattack", slots: [
    { attackIds: ["sword", "bow"], saveActionIds: [] },
    { attackIds: ["sword", "bow"], saveActionIds: [] },
  ] },
};
const rangedHybrid = { ...hybrid, id: "ranged-hybrid", name: "Ranged Hybrid", primary_attack_id: "bow" };
const frontTarget = {
  id: "front", name: "Front", kind: "character", size: "medium", armor_class: 12, max_hp: 30, speed_ft: 30,
  primary_attack_id: "front-sword", traits: [], resources: {}, saving_throw_actions: [],
  attacks: [{ id: "front-sword", name: "Sword", kind: "melee", bonus: 4, reach: 5, diceCount: 1, diceSize: 6, damageBonus: 2, damageType: "slashing" }],
};
const backTarget = {
  id: "back", name: "Back", kind: "character", size: "medium", armor_class: 12, max_hp: 30, speed_ft: 30,
  primary_attack_id: "back-bow", traits: [], resources: {}, saving_throw_actions: [],
  attacks: [
    { id: "back-bow", name: "Bow", kind: "ranged", bonus: 4, normal: 80, long: 320, diceCount: 1, diceSize: 6, damageBonus: 2, damageType: "piercing" },
    { id: "back-sword", name: "Sword", kind: "melee", bonus: 4, reach: 5, diceCount: 1, diceSize: 6, damageBonus: 2, damageType: "slashing" },
  ],
};
const monsterGuard = { ...frontTarget, id: "guard", name: "Guard", kind: "monster", primary_attack_id: "front-sword" };

function hybridSetup() {
  const front = member("hero-front", "heroes", frontTarget, 5);
  const back = member("hero-back", "heroes", backTarget, 0);
  const attacker = member("monster-hybrid", "monsters", hybrid, 10);
  return { setup: { heroes: [front, back], monsters: [attacker] }, attacker, front, back };
}
function rangedHybridSetup(protectedByFrontline) {
  const target = member("hero-front", "heroes", frontTarget, 5);
  const attacker = member("monster-ranged", "monsters", rangedHybrid, 15);
  const guard = member("monster-guard", "monsters", monsterGuard, 10);
  return {
    setup: { heroes: [target], monsters: protectedByFrontline ? [guard, attacker] : [attacker] },
    attacker,
  };
}

{
  const { setup, attacker, front, back } = hybridSetup();
  window.IRON_PIT_DICE = queuedDice([76, 15, 4, 15, 4]);
  const result = T.resolveTurn(1, 1, attacker, setup);
  const attacks = result.events.filter((event) => event.event_type === "attack");
  assert.deepEqual(attacks.map((event) => event.weapon_id), ["sword", "bow"]);
  assert.deepEqual(attacks.map((event) => event.target_id), [front.combatant_id, back.combatant_id]);
  assert.equal(attacks[1].attack_roll.mode, "normal", "Pit split shot must not be taxed by close-range Disadvantage");
}

{
  const { setup, attacker, front } = hybridSetup();
  window.IRON_PIT_DICE = queuedDice([75, 15, 4, 15, 4]);
  const result = T.resolveTurn(1, 1, attacker, setup);
  const attacks = result.events.filter((event) => event.event_type === "attack");
  assert.deepEqual(attacks.map((event) => event.weapon_id), ["sword", "sword"]);
  assert.deepEqual(attacks.map((event) => event.target_id), [front.combatant_id, front.combatant_id]);
}

{
  const { setup, attacker } = rangedHybridSetup(true);
  window.IRON_PIT_DICE = queuedDice([15, 4, 15, 4]);
  const result = T.resolveTurn(1, 1, attacker, setup);
  const attacks = result.events.filter((event) => event.event_type === "attack");
  assert.deepEqual(attacks.map((event) => event.weapon_id), ["bow", "bow"], "screened ranged Multiattack stays ranged");
}

{
  const { setup, attacker } = rangedHybridSetup(false);
  window.IRON_PIT_DICE = queuedDice([15, 4, 15, 4]);
  const result = T.resolveTurn(1, 1, attacker, setup);
  const attacks = result.events.filter((event) => event.event_type === "attack");
  assert.deepEqual(attacks.map((event) => event.weapon_id), ["sword", "sword"], "exposed ranged Multiattack switches to melee");
}

console.log("Browser fixed-formation mixed Multiattack regressions passed.");
