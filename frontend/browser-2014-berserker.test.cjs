"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const name of [
  "browser-heroes.js", "browser-condition-immunity.js", "browser-condition-rules.js",
  "browser-action-economy.js", "browser-grapple.js", "browser-timed-conditions.js",
  "browser-exhaustion.js", "browser-modifiers.js", "browser-state.js", "browser-rage.js",
  "browser-barbarian2.js", "browser-barbarian3.js", "browser-rolls.js", "browser-zero-hp.js",
  "browser-attack.js", "browser-formation.js", "browser-frenzy-2014.js", "browser-saves.js",
  "browser-intimidating-presence-2014.js",
]) load(name);

function queuedDice(values, fallback = 10) {
  const queue = [...values];
  const roll = (sides) => ((queue.length ? queue.shift() : fallback) - 1) % sides + 1;
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
}

function member(template, id, side, position = 0) {
  return { combatant_id: id, side, position_ft: position, state: window.IRON_PIT_BROWSER_STATE.buildState(structuredClone(template)) };
}

const heroes = window.IRON_PIT_BROWSER_HEROES;
const l3 = heroes["rokhan-stonefury-2014-l3"];
const l9 = heroes["rokhan-stonefury-2014-l9"];
const l10 = heroes["rokhan-stonefury-2014-l10"];
assert.ok(l3 && l9 && l10, "generated 2014 Berserker levels 3, 9, and 10 must exist");
for (const hero of [l3, l9, l10]) {
  assert.equal(hero.ruleset, "2014");
  assert.deepEqual(hero.weapon_masteries, []);
  assert.ok(hero.attacks.every((attack) => attack.masteryProperty == null));
}

{
  const state = member(l10, "exhausted", "heroes").state;
  state.exhaustion_level = 3;
  assert.equal(window.IRON_PIT_BROWSER_EXHAUSTION.d20Modifier(state), 0);
  assert.equal(window.IRON_PIT_BROWSER_EXHAUSTION.attackDisadvantage(state), 1);
  assert.equal(window.IRON_PIT_BROWSER_EXHAUSTION.saveDisadvantage(state), 1);
  assert.equal(window.IRON_PIT_BROWSER_EXHAUSTION.effectiveSpeed(state, 40), 20);
  state.exhaustion_level = 4;
  assert.equal(window.IRON_PIT_BROWSER_EXHAUSTION.effectiveMaxHp(state, 100), 50);
  state.exhaustion_level = 5;
  assert.equal(window.IRON_PIT_BROWSER_EXHAUSTION.effectiveSpeed(state, 40), 0);
}

{
  const hero = member(l3, "rokhan", "heroes", 0);
  window.IRON_PIT_BROWSER_STATE.beginTurn(hero.state);
  const rage = window.IRON_PIT_BROWSER_RAGE.enter(1, 1, hero);
  assert.ok(rage);
  assert.ok(hero.state.active_effect_ids.includes("frenzy-2014"));
  assert.equal(hero.state.rage_max_round, 11);
  assert.equal(hero.state.exhaustion_level, 0);
  assert.equal(window.IRON_PIT_BROWSER_RAGE.end(hero.state), 1);
  assert.equal(hero.state.exhaustion_level, 1);
  assert.equal(window.IRON_PIT_BROWSER_RAGE.end(hero.state), null);
  assert.equal(hero.state.exhaustion_level, 1);
}

{
  const state = member(l9, "critical", "heroes").state;
  const greataxe = state.template.attacks.find((attack) => attack.kind === "melee");
  window.IRON_PIT_DICE = queuedDice([6, 7, 8]);
  const damage = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(state, greataxe, true, "normal", "1:critical");
  const brutal = damage.components.find((component) => component.source === "Brutal Critical");
  assert.ok(brutal, "level-9 critical must include Brutal Critical");
  assert.equal(brutal.rolls.length, 1);
  assert.equal(brutal.notation, "1d12+0");
}

{
  const actor = member(l10, "rokhan-presence", "heroes", 0);
  const targetTemplate = structuredClone(heroes["karnok-stoneward-2014-l10"]);
  const target = member(targetTemplate, "target-presence", "monsters", 5);
  window.IRON_PIT_BROWSER_STATE.beginTurn(actor.state);
  window.IRON_PIT_DICE = queuedDice([1]);
  const failed = window.IRON_PIT_BROWSER_INTIMIDATING_PRESENCE_2014.resolve(1, 1, actor, target);
  assert.ok(failed && failed.save_succeeded === false);
  assert.ok(target.state.active_effect_ids.includes("frightened"));

  const actor2 = member(l10, "rokhan-presence-2", "heroes", 0);
  const target2 = member(targetTemplate, "target-presence-2", "monsters", 5);
  window.IRON_PIT_BROWSER_STATE.beginTurn(actor2.state);
  window.IRON_PIT_DICE = queuedDice([20]);
  const succeeded = window.IRON_PIT_BROWSER_INTIMIDATING_PRESENCE_2014.resolve(1, 1, actor2, target2);
  assert.ok(succeeded && succeeded.save_succeeded === true);
  actor2.state.action_available = true;
  assert.equal(window.IRON_PIT_BROWSER_INTIMIDATING_PRESENCE_2014.canUse(actor2, target2), false);
}

console.log("2014 Berserker browser mechanics stay edition-isolated and RAW-certified through level 10.");
