"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
load("browser-heroes.js");
load("browser-condition-immunity.js");
load("browser-condition-rules.js");
load("browser-action-economy.js");
load("browser-state.js");
load("browser-rage.js");
load("browser-rolls.js");

const heroes = window.IRON_PIT_BROWSER_HEROES;
const levels = Array.from({ length: 10 }, (_, index) => heroes[`rokhan-stonefury-2014-l${index + 1}`]);
assert.ok(levels.every(Boolean), "all ten 2014 Berserker levels must be exported");
for (const hero of levels) {
  assert.equal(hero.ruleset, "2014");
  assert.equal(hero.build_id, "canonical-2014");
  assert.deepEqual(hero.weapon_masteries, []);
  assert.ok(hero.attacks.every((attack) => attack.masteryProperty == null));
}
assert.equal(levels[2].frenzy_bonus_attack_2014, true);
assert.equal(levels[2].frenzy, false, "2014 Berserker must not receive the 2024 Frenzy damage rider");
assert.equal(levels[5].mindless_rage, true);
assert.equal(levels[6].initiative_advantage, true);
assert.equal(levels[8].melee_critical_extra_weapon_dice, 2);
assert.equal(levels[9].intimidating_presence_2014, true);

function queuedDice(values) {
  const queue = [...values];
  const roll = (sides) => {
    const value = queue.shift();
    if (value == null || value < 1 || value > sides) throw new Error(`invalid queued d${sides} value`);
    return value;
  };
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
}

{
  const state = window.IRON_PIT_BROWSER_STATE.buildState(structuredClone(levels[0]));
  const greataxe = state.template.attacks.find((attack) => attack.name === "Greataxe");
  window.IRON_PIT_DICE = queuedDice([1, 2, 3]);
  const result = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(state, greataxe, true, "normal", "1:rokhan");
  assert.equal(result.roll.total, 9);
  assert.equal(result.components[0].notation, "2d12+3");
  assert.equal(result.components[1].notation, "1d12+0", "Half-Orc Savage Attacks adds one weapon die");
}

{
  const state = window.IRON_PIT_BROWSER_STATE.buildState(structuredClone(levels[8]));
  const greataxe = state.template.attacks.find((attack) => attack.name === "Greataxe");
  window.IRON_PIT_DICE = queuedDice([1, 2, 3, 4]);
  const result = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(state, greataxe, true, "normal", "1:rokhan");
  assert.equal(result.roll.total, 15);
  assert.equal(result.components[1].notation, "2d12+0", "Savage Attacks and Brutal Critical add two weapon dice at level 9");
}

{
  const member = { combatant_id: "rokhan", side: "heroes", state: window.IRON_PIT_BROWSER_STATE.buildState(structuredClone(levels[0])) };
  window.IRON_PIT_BROWSER_STATE.beginTurn(member.state);
  assert.ok(window.IRON_PIT_BROWSER_RAGE.enter(1, 1, member));
  assert.equal(window.IRON_PIT_BROWSER_RAGE.active(member.state), true);
  window.IRON_PIT_BROWSER_RAGE.finalize(2, 1, member);
  assert.equal(window.IRON_PIT_BROWSER_RAGE.active(member.state), false, "2014 Rage ends on a turn with no attack and no damage");
}

{
  const member = { combatant_id: "rokhan", side: "heroes", state: window.IRON_PIT_BROWSER_STATE.buildState(structuredClone(levels[2])) };
  const target = { combatant_id: "target", side: "monsters", state: { current_hp: 10, is_alive: true, is_dead: false } };
  const greataxe = member.state.template.attacks.find((attack) => attack.name === "Greataxe");
  const setup = { heroes: [member], monsters: [target] };
  window.IRON_PIT_BROWSER_FORMATION = { chooseAttack: () => ({ target, attack: greataxe, distance: 5 }) };
  window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION = {
    resolve: (sequence) => ({ events: [{ sequence, description: "Rokhan attacks." }], sequence: sequence + 1 }),
  };

  window.IRON_PIT_BROWSER_STATE.beginTurn(member.state);
  window.IRON_PIT_BROWSER_RAGE.enter(1, 1, member);
  window.IRON_PIT_BROWSER_RAGE.extendFromAttack(member.state, 1);
  window.IRON_PIT_BROWSER_RAGE.finalize(2, 1, member);
  assert.equal(member.state.bonus_action_available, false, "entering Rage spends the entry-turn Bonus Action");

  window.IRON_PIT_BROWSER_STATE.beginTurn(member.state);
  assert.equal(member.state.bonus_action_available, true);
  const frenzy = window.IRON_PIT_BROWSER_RAGE.resolveFrenzyAttack(3, 2, member, setup, "2:rokhan");
  assert.ok(frenzy);
  assert.equal(member.state.bonus_action_available, false, "2014 Frenzy spends one Bonus Action");
  assert.match(frenzy.events[0].description, /2014 Frenzy uses the Bonus Action melee attack/);
}

console.log("Browser 2014 Berserker regressions passed.");