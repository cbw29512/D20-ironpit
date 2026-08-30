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
  "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js", "browser-grapple.js",
  "browser-timed-conditions.js", "browser-state.js", "browser-rage.js", "browser-rolls.js", "browser-attack.js",
  "browser-reactions.js", "browser-reaction-movement.js", "browser-saves.js", "browser-condition-lifecycle.js",
  "browser-charge.js", "browser-multiattack.js", "browser-healing.js", "browser-spellcasting.js",
  "browser-condition-removal.js", "browser-support.js", "browser-turn.js", "browser-engine.js",
]) load(file);

const queuedDice = (values, fallback = 10) => {
  const queue = [...values];
  const roll = (sides) => ((queue.length ? queue.shift() : fallback) - 1) % sides + 1;
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
};
const deterministicDice = (seed = 99) => {
  let state = seed >>> 0;
  const roll = (sides) => { state = (1664525 * state + 1013904223) >>> 0; return (state % sides) + 1; };
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
};
const S = window.IRON_PIT_BROWSER_STATE;
const A = window.IRON_PIT_BROWSER_ATTACK;
const heroes = window.IRON_PIT_BROWSER_HEROES;
const monsters = window.IRON_PIT_BROWSER_MONSTERS;
const member = (id, side, template, position = side === "heroes" ? 0 : 5) => ({
  combatant_id: id, side, position_ft: position, state: S.buildState(structuredClone(template)),
});

assert.equal(Object.keys(monsters).length, 62, "venom batch must bring browser roster to 62 monsters");

{
  const snake = monsters["srd-giant-venomous-snake"], bite = snake.attacks[0];
  assert.equal(snake.armor_class, 14); assert.equal(snake.max_hp, 11); assert.equal(snake.speed_ft, 40); assert.equal(snake.initiative_bonus, 4);
  assert.equal(bite.bonus, 6); assert.equal(bite.reach, 10); assert.equal(bite.diceSize, 4); assert.equal(bite.damageBonus, 4);
  assert.deepEqual(bite.onHitDamage, [{ source: "Venom", diceCount: 1, diceSize: 8, damageBonus: 0, damageType: "poison" }]);
}

{
  const wasp = monsters["srd-giant-wasp"], sting = wasp.attacks[0];
  assert.equal(wasp.armor_class, 13); assert.equal(wasp.max_hp, 22); assert.equal(wasp.speed_ft, 50); assert.equal(wasp.initiative_bonus, 2);
  assert.equal(sting.bonus, 4); assert.equal(sting.diceSize, 6); assert.equal(sting.damageBonus, 2);
  assert.equal(sting.onHitDamage[0].diceCount, 2); assert.equal(sting.onHitDamage[0].diceSize, 4);
}

{
  const spider = monsters["srd-giant-wolf-spider"], bite = spider.attacks[0];
  assert.equal(spider.armor_class, 13); assert.equal(spider.max_hp, 11); assert.equal(spider.speed_ft, 40); assert.equal(spider.initiative_bonus, 3);
  assert.equal(bite.bonus, 5); assert.equal(bite.diceSize, 4); assert.equal(bite.damageBonus, 3);
  assert.equal(bite.onHitDamage[0].diceCount, 2); assert.equal(bite.onHitDamage[0].diceSize, 4);
}

{
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
  const snake = member("monster-1:snake", "monsters", monsters["srd-giant-venomous-snake"]);
  window.IRON_PIT_DICE = queuedDice([15, 2, 6]);
  const event = A.resolveAttack(1, 1, snake, hero, snake.state.template.attacks[0], 5);
  assert.equal(event.hit, true);
  assert.deepEqual(event.damage_components.map((part) => part.damage_type), ["piercing", "poison"]);
  assert.deepEqual(event.damage_components.map((part) => part.total), [6, 6]);
  assert.equal(event.damage_roll.total, 12);
}

{
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
  const wasp = member("monster-1:wasp", "monsters", monsters["srd-giant-wasp"]);
  hero.state.template.damage_immunities = ["poison"];
  window.IRON_PIT_DICE = queuedDice([15, 3, 4, 4]);
  const event = A.resolveAttack(1, 1, wasp, hero, wasp.state.template.attacks[0], 5);
  assert.deepEqual(event.damage_components.map((part) => part.total), [5, 8]);
  assert.deepEqual(event.damage_components.map((part) => part.applied_total), [5, 0]);
  assert.equal(event.damage_roll.total, 5);
}

{
  window.IRON_PIT_DICE = deterministicDice(41);
  const battle = window.IRON_PIT_BROWSER_ENGINE.runEncounter({
    hero_ids: ["karnok-stoneward-l1"], monster_ids: ["srd-giant-wolf-spider"], starting_distance_ft: 30,
  });
  assert.notEqual(battle.outcome, "active");
  assert.ok(battle.events.some((event) => event.event_type === "attack" && event.actor_id.startsWith("monster-")));
  assert.ok(battle.events.some((event) => event.damage_components?.some((part) => part.damage_type === "poison")));
}

console.log("Browser SRD venom monster regressions passed.");
