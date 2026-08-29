"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters.js", "browser-monsters-fixed.js", "browser-monsters-beast2.js",
  "browser-monsters-batch3.js", "browser-state.js", "browser-rage.js", "browser-rolls.js", "browser-attack.js",
  "browser-charge.js", "browser-multiattack.js", "browser-turn.js", "browser-engine.js",
]) load(file);

const maxDice = { roll: (sides) => sides, rollMany: (count, sides) => Array(count).fill(sides) };
const queuedDice = (values, fallback = 10) => {
  const queue = [...values];
  const roll = (sides) => ((queue.length ? queue.shift() : fallback) - 1) % sides + 1;
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
};

const S = window.IRON_PIT_BROWSER_STATE;
const A = window.IRON_PIT_BROWSER_ATTACK;
const T = window.IRON_PIT_BROWSER_TURN;
const heroes = window.IRON_PIT_BROWSER_HEROES;
const monsters = window.IRON_PIT_BROWSER_MONSTERS;

{
  const hero = { combatant_id: "hero-1:karnok", side: "heroes", position_ft: 0, state: S.buildState(structuredClone(heroes["karnok-stoneward-l1"])) };
  const monster = { combatant_id: "monster-1:commoner", side: "monsters", position_ft: 5, state: S.buildState(structuredClone(monsters["srd-commoner"])) };
  hero.state.current_hp = 0; hero.state.is_unconscious = true;
  assert.equal(S.nearestTarget(monster, { heroes: [hero], monsters: [monster] }), hero, "downed living hero remains targetable when nobody stands");
}

{
  const hero = { combatant_id: "hero-1:karnok", side: "heroes", position_ft: 0, state: S.buildState(structuredClone(heroes["karnok-stoneward-l1"])) };
  hero.state.active_effect_ids.push("dodge");
  A.applyDamage(hero.state, hero.state.current_hp, false);
  assert.equal(hero.state.is_unconscious, true);
  assert.ok(hero.state.active_effect_ids.includes("prone"), "Unconscious must include Prone");
  assert.ok(!hero.state.active_effect_ids.includes("dodge"), "Dodge benefit must end when Incapacitated");
}

{
  const hero = { combatant_id: "hero-1:karnok", side: "heroes", position_ft: 0, state: S.buildState(structuredClone(heroes["karnok-stoneward-l1"])) };
  A.applyDamage(hero.state, hero.state.current_hp, false);
  hero.state.death_save_successes = 2;
  A.applyDamage(hero.state, 1, false);
  assert.equal(hero.state.death_save_successes, 2, "damage at 0 HP must not erase existing Death Save successes");
  assert.equal(hero.state.death_save_failures, 1);
}

{
  const member = { combatant_id: "hero-1:karnok", side: "heroes", position_ft: 0, state: S.buildState(structuredClone(heroes["karnok-stoneward-l1"])) };
  A.applyDamage(member.state, member.state.current_hp, false);
  window.IRON_PIT_DICE = queuedDice([20]);
  T.deathSave(1, 1, member);
  assert.equal(member.state.current_hp, 1);
  assert.equal(member.state.is_unconscious, false);
  assert.ok(member.state.active_effect_ids.includes("prone"), "ending Unconscious after a natural 20 must leave Prone");
}

{
  const hero = { combatant_id: "hero-1:karnok", side: "heroes", position_ft: 0, state: S.buildState(structuredClone(heroes["karnok-stoneward-l1"])) };
  const monster = { combatant_id: "monster-1:commoner", side: "monsters", position_ft: 5, state: S.buildState(structuredClone(monsters["srd-commoner"])) };
  A.applyDamage(hero.state, hero.state.current_hp, false);
  window.IRON_PIT_DICE = queuedDice([19, 19, 1, 1]);
  const event = A.resolveAttack(1, 1, monster, hero, monster.state.template.attacks[0], 5);
  assert.equal(event.attack_roll.mode, "advantage");
  assert.equal(event.attack_roll.selected_roll, 19);
  assert.equal(event.critical, true, "a hit from within 5 feet against Unconscious must be critical");
  assert.equal(hero.state.death_save_failures, 2);
}

{
  window.IRON_PIT_DICE = maxDice;
  const battle = window.IRON_PIT_BROWSER_ENGINE.runEncounter({
    hero_ids: ["karnok-stoneward-l1"], monster_ids: ["srd-ogre"], starting_distance_ft: 5,
  });
  assert.equal(battle.outcome, "monsters_win");
  assert.equal(battle.setup.heroes[0].state.is_dead, true, "monster victory must be actual character death, not merely 0 HP");
}

{
  window.IRON_PIT_DICE = queuedDice([10, 15, 10, 10], 20);
  const battle = window.IRON_PIT_BROWSER_ENGINE.runEncounter({
    hero_ids: ["karnok-stoneward-l1"], monster_ids: ["srd-scout"], starting_distance_ft: 30,
  });
  const scoutAttacks = battle.events.filter((event) => event.event_type === "attack" && event.actor_id.startsWith("monster-1:"));
  const scoutMove = battle.events.find((event) => event.event_type === "movement" && event.actor_id.startsWith("monster-1:"));
  assert.deepEqual(scoutAttacks.slice(0, 2).map((event) => event.weapon_id), ["scout-longbow", "scout-longbow"]);
  assert.ok(scoutMove && scoutMove.distance_after_ft === 5, "ranged multiattack must spend remaining movement closing into melee");
}

console.log("Browser melee deathmatch regressions passed.");
