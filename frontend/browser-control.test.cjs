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
  "browser-rage.js", "browser-rolls.js", "browser-attack.js", "browser-saves.js", "browser-charge.js",
  "browser-multiattack.js", "browser-turn.js", "browser-engine.js",
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
  window.IRON_PIT_DICE = queuedDice([15, 1]);
  const event = A.resolveAttack(1, 1, croc, hero, croc.state.template.attacks[0], 5);
  assert.equal(event.hit, true);
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
  assert.equal(S.nearestTarget(crab, { heroes: [held, other], monsters: [crab] }), held);
  crab.state.is_dead = true; crab.state.is_alive = false;
  G.cleanup({ heroes: [held, other], monsters: [crab] });
  assert.equal(held.state.grapple_sources.length, 0);
}

{
  const state = S.buildState(structuredClone(heroes["karnok-stoneward-l1"]));
  window.IRON_PIT_DICE = queuedDice([20]);
  const high = V.resolveSavingThrow(state, "intelligence", 20);
  assert.equal(high.roll.total, 19); assert.equal(high.succeeded, false);
  window.IRON_PIT_DICE = queuedDice([1]);
  const low = V.resolveSavingThrow(state, "strength", 6);
  assert.equal(low.roll.total, 6); assert.equal(low.succeeded, true);
}

{
  const state = S.buildState(structuredClone(heroes["karnok-stoneward-l1"]));
  state.active_effect_ids.push("restrained");
  window.IRON_PIT_DICE = queuedDice([18, 2]);
  const save = V.resolveSavingThrow(state, "dexterity", 10);
  assert.equal(save.roll.mode, "disadvantage"); assert.equal(save.roll.selected_roll, 2);
}

{
  const state = S.buildState(structuredClone(heroes["rokhan-stonefury-l1"]));
  state.active_effect_ids.push("rage");
  window.IRON_PIT_DICE = queuedDice([2, 10]);
  const save = V.resolveSavingThrow(state, "strength", 12);
  assert.equal(save.roll.mode, "advantage"); assert.equal(save.roll.selected_roll, 10);
}

{
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
  const snake = member("monster-1:snake", "monsters", monsters["srd-constrictor-snake"]);
  const action = snake.state.template.saving_throw_actions[0];
  window.IRON_PIT_DICE = queuedDice([1, 1, 2, 3]);
  const failed = V.resolveAction(1, 1, snake, hero, action, 5);
  assert.equal(failed.save_succeeded, false); assert.equal(failed.damage_roll.total, 6);
  assert.deepEqual(failed.applied_condition_ids, ["grappled"]);
  assert.equal(hero.state.current_hp, 6);
}

{
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
  const snake = member("monster-1:snake", "monsters", monsters["srd-constrictor-snake"]);
  const action = snake.state.template.saving_throw_actions[0];
  window.IRON_PIT_DICE = queuedDice([10, 1, 1, 1]);
  const passed = V.resolveAction(1, 1, snake, hero, action, 5);
  assert.equal(passed.save_succeeded, true); assert.equal(passed.damage_roll.total, 0);
  assert.equal(hero.state.current_hp, hero.state.template.max_hp);
  assert.equal(hero.state.grapple_sources.length, 0);
}

console.log("Browser saving throw and control-condition regressions passed.");
