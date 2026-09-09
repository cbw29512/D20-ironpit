"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters.js", "browser-monsters-fixed.js", "browser-monsters-beast2.js",
  "browser-monsters-batch3.js", "browser-monsters-control.js", "browser-grapple.js", "browser-state.js",
  "browser-rage.js", "browser-rolls.js", "browser-zero-hp.js", "browser-attack.js", "browser-resources.js", "browser-saves.js", "browser-charge.js",
  "browser-formation.js", "browser-multiattack.js", "browser-turn.js", "browser-engine.js",
]) load(file);

const queuedDice = (values, fallback = 10) => {
  const queue = [...values];
  const roll = (sides) => ((queue.length ? queue.shift() : fallback) - 1) % sides + 1;
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
};
const S = window.IRON_PIT_BROWSER_STATE;
const A = window.IRON_PIT_BROWSER_ATTACK;
const G = window.IRON_PIT_BROWSER_GRAPPLE;
const V = window.IRON_PIT_BROWSER_SAVES;
const heroes = window.IRON_PIT_BROWSER_HEROES;
const monsters = window.IRON_PIT_BROWSER_MONSTERS;
const member = (id, side, template, position = side === "heroes" ? 0 : 5) => ({
  combatant_id: id, side, position_ft: position, state: S.buildState(structuredClone(template)),
});

assert.equal(Object.keys(monsters).length, 58, "control batch must bring browser roster to 58 monsters");

{
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
  const croc = member("monster-1:crocodile", "monsters", monsters["srd-crocodile"]);
  hero.state.active_effect_ids.push("dodge");
  window.IRON_PIT_DICE = queuedDice([15, 15, 1]);
  const event = A.resolveAttack(1, 1, croc, hero, croc.state.template.attacks[0], 5);
  assert.equal(event.hit, true);
  assert.equal(event.attack_roll.mode, "disadvantage");
  assert.deepEqual(event.applied_condition_ids, ["grappled", "restrained"]);
  assert.equal(G.speedIsZero(hero.state), true);
  assert.equal(hero.state.active_effect_ids.includes("dodge"), false);
  assert.equal(hero.state.grapple_sources[0].escape_dc, 12);
}

{
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
  const crab = member("monster-1:crab", "monsters", monsters["srd-giant-crab"]);
  const commoner = member("monster-2:commoner", "monsters", monsters["srd-commoner"]);
  const setup = { heroes: [hero], monsters: [crab, commoner] };
  G.apply(hero.state, crab.combatant_id, 11, 5, false);
  assert.equal(G.attackDisadvantage(hero.state, crab.combatant_id), 0);
  assert.equal(G.attackDisadvantage(hero.state, commoner.combatant_id), 1);
  assert.equal(S.nearestTarget(hero, setup), crab);
}

{
  const held = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
  const other = member("hero-2:rokhan", "heroes", heroes["rokhan-stonefury-l1"]);
  const crab = member("monster-1:crab", "monsters", monsters["srd-giant-crab"]);
  G.apply(held.state, crab.combatant_id, 11, 5, false);
  held.state.current_hp = 0; held.state.is_unconscious = true;
  assert.equal(
    S.nearestTarget(crab, { heroes: [held, other], monsters: [crab] }),
    other,
    "an active combatant must be targeted before an Unconscious disabled target",
  );
  crab.state.is_dead = true; crab.state.is_alive = false;
  assert.equal(G.releaseForSource({ heroes: [held, other], monsters: [crab] }, crab.combatant_id), 1);
  assert.equal(G.speedIsZero(held.state), false);
}

{
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
  const crab = member("monster-1:crab", "monsters", monsters["srd-giant-crab"]);
  const setup = { heroes: [hero], monsters: [crab] };
  G.apply(hero.state, crab.combatant_id, 11, 5, false);
  window.IRON_PIT_DICE = queuedDice([12]);
  const events = G.resolveEscapeAction(1, 1, hero, setup);
  assert.equal(events.length, 1); assert.equal(events[0].type, "grapple_escape");
  assert.equal(events[0].success, true); assert.equal(G.speedIsZero(hero.state), false);
}

{
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
  const giantFrog = member("monster-1:frog", "monsters", monsters["srd-giant-frog"]);
  window.IRON_PIT_DICE = queuedDice([15, 4]);
  const event = A.resolveAttack(1, 1, giantFrog, hero, giantFrog.state.template.attacks[0], 5);
  assert.equal(event.hit, true);
  assert.deepEqual(event.applied_condition_ids, ["grappled"]);
  assert.equal(hero.state.grapple_sources[0].escape_dc, 11);
}

{
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
  const constrictor = member("monster-1:snake", "monsters", monsters["srd-constrictor-snake"]);
  window.IRON_PIT_DICE = queuedDice([15, 4]);
  const event = A.resolveAttack(1, 1, constrictor, hero, constrictor.state.template.attacks[0], 5);
  assert.equal(event.hit, true);
  assert.deepEqual(event.applied_condition_ids, ["grappled", "restrained"]);
  assert.equal(hero.state.grapple_sources[0].escape_dc, 12);
}

{
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
  const spider = member("monster-1:spider", "monsters", monsters["srd-giant-spider"]);
  const web = spider.state.template.saving_throw_actions[0];
  window.IRON_PIT_DICE = queuedDice([1]);
  const event = V.resolveAction(1, 1, spider, hero, web, 30);
  assert.equal(event.save_succeeded, false);
  assert.deepEqual(event.applied_condition_ids, ["restrained"]);
}

console.log("Browser monster control and grapple regressions passed.");