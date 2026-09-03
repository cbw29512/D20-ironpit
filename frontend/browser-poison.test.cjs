"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters.js", "browser-monsters-fixed.js", "browser-monsters-beast2.js",
  "browser-monsters-batch3.js", "browser-monsters-control.js", "browser-monsters-poison.js", "browser-condition-immunity.js",
  "browser-grapple.js", "browser-timed-conditions.js", "browser-state.js", "browser-rage.js", "browser-rolls.js",
  "browser-zero-hp.js", "browser-attack.js",
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

assert.equal(Object.keys(monsters).length, 59, "poison batch must preserve the legacy browser fixture roster");

{
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
  const centipede = member("monster-1:centipede", "monsters", monsters["srd-giant-centipede"]);
  const attack = centipede.state.template.attacks[0];
  assert.equal(attack.controlEffect.conditionId, "poisoned");
  window.IRON_PIT_DICE = queuedDice([15, 1]);
  const event = A.resolveAttack(1, 1, centipede, hero, attack, 5);
  assert.equal(event.hit, true);
  assert.deepEqual(event.applied_condition_ids, ["poisoned"]);
  const poison = hero.state.timed_effects[0];
  assert.equal(poison.expiry_timing, null);
  assert.equal(poison.expires_at_start_of_source_turn, false);
  assert.equal(poison.repeat_save_ability, "constitution");
  assert.equal(poison.repeat_save_dc, 10);
  assert.equal(poison.repeat_save_timing, "target_turn_start");

  window.IRON_PIT_DICE = queuedDice([18, 2, 3, 3, 3, 3]);
  const counter = A.resolveAttack(2, 1, hero, centipede, hero.state.template.attacks[0], 5);
  assert.equal(counter.attack_roll.mode, "disadvantage");
  assert.equal(counter.attack_roll.selected_roll, 2);
}

{
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
  const first = member("monster-1:centipede", "monsters", monsters["srd-giant-centipede"]);
  const second = member("monster-2:centipede", "monsters", monsters["srd-giant-centipede"]);
  T.apply(hero.state, "poisoned", first.combatant_id);
  T.apply(hero.state, "poisoned", second.combatant_id);
  assert.equal(hero.state.active_effect_ids.filter((id) => id === "poisoned").length, 1);
  assert.equal(hero.state.timed_effects.filter((effect) => effect.effect_id === "poisoned").length, 1);
}

{
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
  const centipede = member("monster-1:centipede", "monsters", monsters["srd-giant-centipede"]);
  hero.state.active_buff_effect_ids.push("protection-from-poison");
  assert.equal(T.apply(hero.state, "poisoned", centipede.combatant_id), null);
  assert.equal(hero.state.active_effect_ids.includes("poisoned"), false);
}

{
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
  const centipede = member("monster-1:centipede", "monsters", monsters["srd-giant-centipede"]);
  T.apply(hero.state, "poisoned", centipede.combatant_id);
  G.apply(hero.state, centipede.combatant_id, 12, 5, true);
  window.IRON_PIT_DICE = queuedDice([18, 2]);
  const escape = G.escape(1, 1, hero);
  assert.equal(escape.ability_check_roll.mode, "disadvantage");
  assert.equal(escape.ability_check_roll.selected_roll, 2);
}

console.log("Browser universal Poisoned policy regressions passed.");
require("./browser-poison-expansion.test.cjs");
