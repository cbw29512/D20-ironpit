"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters.js", "browser-monsters-fixed.js", "browser-monsters-beast2.js",
  "browser-monsters-batch3.js", "browser-monsters-control.js", "browser-monsters-poison.js", "browser-grapple.js",
  "browser-timed-conditions.js", "browser-state.js", "browser-rage.js", "browser-rolls.js", "browser-zero-hp.js", "browser-attack.js",
]) load(file);

const queuedDice = (values, fallback = 10) => {
  const queue = [...values];
  const roll = (sides) => ((queue.length ? queue.shift() : fallback) - 1) % sides + 1;
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
};
const S = window.IRON_PIT_BROWSER_STATE;
const A = window.IRON_PIT_BROWSER_ATTACK;
const G = window.IRON_PIT_BROWSER_GRAPPLE;
const T = window.IRON_PIT_BROWSER_TIMED;
const heroes = window.IRON_PIT_BROWSER_HEROES;
const monsters = window.IRON_PIT_BROWSER_MONSTERS;
const member = (id, side, template, position = side === "heroes" ? 0 : 5) => ({
  combatant_id: id, side, position_ft: position, state: S.buildState(structuredClone(template)),
});
const sourceStartExpiry = { expiresAtStartOfSourceTurn: true };

assert.equal(Object.keys(monsters).length, 59, "poison batch must bring browser roster to 59 monsters");

{
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
  const centipede = member("monster-1:centipede", "monsters", monsters["srd-giant-centipede"]);
  const attack = centipede.state.template.attacks[0];
  assert.equal(centipede.state.template.armor_class, 14);
  assert.equal(centipede.state.template.max_hp, 9);
  assert.equal(attack.bonus, 4);
  assert.equal(attack.controlEffect.conditionId, "poisoned");

  window.IRON_PIT_DICE = queuedDice([15, 1]);
  const event = A.resolveAttack(1, 1, centipede, hero, attack, 5);
  assert.equal(event.hit, true);
  assert.deepEqual(event.applied_condition_ids, ["poisoned"]);
  assert.equal(hero.state.active_effect_ids.includes("poisoned"), true);
  assert.equal(hero.state.timed_effects[0].source_id, centipede.combatant_id);

  window.IRON_PIT_DICE = queuedDice([18, 2, 3, 3, 3, 3]);
  const counter = A.resolveAttack(2, 1, hero, centipede, hero.state.template.attacks[0], 5);
  assert.equal(counter.attack_roll.mode, "disadvantage");
  assert.equal(counter.attack_roll.selected_roll, 2);
}

{
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
  const centipede = member("monster-1:centipede", "monsters", monsters["srd-giant-centipede"]);
  T.apply(hero.state, "poisoned", centipede.combatant_id, sourceStartExpiry);
  G.apply(hero.state, centipede.combatant_id, 12, 5, true);
  window.IRON_PIT_DICE = queuedDice([18, 2]);
  const escape = G.escape(1, 1, hero);
  assert.equal(escape.ability_check_roll.mode, "disadvantage");
  assert.equal(escape.ability_check_roll.selected_roll, 2);
}

{
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
  const centipede = member("monster-1:centipede", "monsters", monsters["srd-giant-centipede"]);
  T.apply(hero.state, "poisoned", centipede.combatant_id, sourceStartExpiry);
  centipede.state.current_hp = 0; centipede.state.is_alive = false; centipede.state.is_dead = true;
  const expired = T.expireSourceStart(4, 2, centipede, { heroes: [hero], monsters: [centipede] });
  assert.equal(expired.events.length, 1);
  assert.deepEqual(expired.events[0].removed_condition_ids, ["poisoned"]);
  assert.equal(hero.state.active_effect_ids.includes("poisoned"), false);
  assert.equal(hero.state.timed_effects.length, 0);
}

{
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
  const first = member("monster-1:centipede", "monsters", monsters["srd-giant-centipede"]);
  const second = member("monster-2:centipede", "monsters", monsters["srd-giant-centipede"]);
  const setup = { heroes: [hero], monsters: [first, second] };
  T.apply(hero.state, "poisoned", first.combatant_id, sourceStartExpiry);
  T.apply(hero.state, "poisoned", second.combatant_id, sourceStartExpiry);
  const firstExpiry = T.expireSourceStart(1, 2, first, setup);
  assert.equal(firstExpiry.events.length, 0);
  assert.equal(hero.state.active_effect_ids.includes("poisoned"), true);
  const secondExpiry = T.expireSourceStart(firstExpiry.sequence, 2, second, setup);
  assert.equal(secondExpiry.events.length, 1);
  assert.equal(hero.state.active_effect_ids.includes("poisoned"), false);
}

console.log("Browser Poisoned and timed-condition regressions passed.");
require("./browser-poison-expansion.test.cjs");
