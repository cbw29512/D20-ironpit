"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
const setDice = (values) => {
  const queue = [...values];
  window.IRON_PIT_DICE = {
    roll: (sides) => {
      assert.ok(queue.length, `fixed dice exhausted before d${sides}`);
      const value = queue.shift();
      assert.ok(value >= 1 && value <= sides, `${value} is invalid for d${sides}`);
      return value;
    },
    rollMany: (count, sides) => Array.from({ length: count }, () => window.IRON_PIT_DICE.roll(sides)),
  };
};

load("browser-heroic-inspiration.js");

const template = { heroic_warrior: true, name: "Karnok", max_hp: 104, speed_ft: 30, traits: [] };
const plainState = () => ({ template, heroic_inspiration: false });

{
  const state = plainState();
  assert.equal(window.IRON_PIT_BROWSER_HEROIC_INSPIRATION.grant(state), true);
  assert.equal(state.heroic_inspiration, true);
  assert.equal(window.IRON_PIT_BROWSER_HEROIC_INSPIRATION.grant(state), false);
}

{
  const state = plainState(); state.heroic_inspiration = true; setDice([8]);
  const result = window.IRON_PIT_BROWSER_HEROIC_INSPIRATION.rerollFailedAttack(
    state, { notation: "1d20", rolls: [5], modifier: 9, selected_roll: 5, mode: "normal", total: 14 }, 17,
  );
  assert.equal(result.used, true); assert.deepEqual(result.roll.rolls, [8]); assert.equal(result.roll.total, 17);
  assert.equal(state.heroic_inspiration, false); assert.match(result.roll.notation, /Heroic Inspiration/);
}

{
  const state = plainState(); state.heroic_inspiration = true; setDice([1]);
  const result = window.IRON_PIT_BROWSER_HEROIC_INSPIRATION.rerollFailedAttack(
    state, { notation: "1d20", rolls: [7], modifier: 9, selected_roll: 7, mode: "normal", total: 16 }, 17,
  );
  assert.equal(result.roll.selected_roll, 1); assert.equal(result.roll.total, 10); assert.equal(state.heroic_inspiration, false);
}

{
  const state = plainState(); state.heroic_inspiration = true; setDice([10]);
  const result = window.IRON_PIT_BROWSER_HEROIC_INSPIRATION.rerollFailedAttack(
    state, { notation: "2d20", rolls: [4, 7], modifier: 9, selected_roll: 7, mode: "advantage", total: 16 }, 17,
  );
  assert.deepEqual(result.roll.rolls, [10, 7]); assert.equal(result.roll.selected_roll, 10); assert.equal(result.roll.total, 19);
}

{
  const state = plainState(); state.heroic_inspiration = true; setDice([10]);
  const result = window.IRON_PIT_BROWSER_HEROIC_INSPIRATION.rerollFailedAttack(
    state, { notation: "2d20", rolls: [7, 18], modifier: 9, selected_roll: 7, mode: "disadvantage", total: 16 }, 17,
  );
  assert.equal(result.used, true); assert.deepEqual(result.roll.rolls, [10, 18]); assert.equal(result.roll.total, 19);
  const impossible = plainState(); impossible.heroic_inspiration = true;
  const unchanged = window.IRON_PIT_BROWSER_HEROIC_INSPIRATION.rerollFailedAttack(
    impossible, { notation: "2d20", rolls: [7, 6], modifier: 9, selected_roll: 6, mode: "disadvantage", total: 15 }, 17,
  );
  assert.equal(unchanged.used, false); assert.equal(impossible.heroic_inspiration, true);
}

window.IRON_PIT_BROWSER_GRAPPLE = { speedIsZero: () => false, attackDisadvantage: () => 0, apply: () => [] };
window.IRON_PIT_BROWSER_MODIFIERS = {
  effectiveSpeed: (state) => state.template.speed_ft, effectiveArmorClass: (state) => state.template.armor_class,
  attacksAgainstAdvantage: () => 0, consumeAttacksAgainstAdvantage: () => 0, nextAttackAgainstAdvantage: () => 0,
  consumeNextAttackAgainstAdvantage: () => 0, applyD20Bonus: (_state, _kind, roll) => roll,
};
window.IRON_PIT_BROWSER_CONDITION_RULES = {
  incapacitated: (state) => state.is_unconscious, has: (state, id) => state.active_effect_ids.includes(id),
  attackAdvantage: () => false, autoCritical: () => false,
};
load("browser-state.js");
{
  const downed = window.IRON_PIT_BROWSER_STATE.buildState({ ...template, armor_class: 17, kind: "character" });
  downed.current_hp = 0; downed.is_unconscious = true; downed.reaction_available = false;
  window.IRON_PIT_BROWSER_STATE.refreshStartOfTurn(downed);
  assert.equal(downed.reaction_available, true); assert.equal(downed.heroic_inspiration, true);
}

window.IRON_PIT_BROWSER_TIMED = { apply: () => null };
window.IRON_PIT_BROWSER_SAP = { applyWeapon: () => false, consume: () => 0, disadvantage: () => 0 };
window.IRON_PIT_BROWSER_TACTICAL_MASTER = { apply: () => false };
window.IRON_PIT_BROWSER_GRAZE = { rawDamage: () => null };
window.IRON_PIT_BROWSER_BARBARIAN2 = { activate: () => false, attackAdvantage: () => 0, attacksAgainstAdvantage: () => 0 };
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_CONCENTRATION = { endIfIncapacitated: () => {} };
window.IRON_PIT_ACTION_ECONOMY = { available: () => true, spend: () => {} };
window.IRON_PIT_BROWSER_RAGE = { damageBonus: () => 0, extendFromAttack: () => {}, endIfIncapacitated: () => {} };
window.IRON_PIT_BROWSER_ZERO_HP = { applyDamage: (state, amount) => { state.current_hp = Math.max(0, state.current_hp - amount); return null; } };
window.IRON_PIT_BROWSER_CHAMPION = { criticalMove: (_attacker, _setup, event) => event };
load("browser-rolls.js");
load("browser-attack.js");

{
  const fighterTemplate = {
    ...template, armor_class: 17, kind: "character", size: "medium", critical_hit_minimum: 19,
    damage_immunities: [], damage_resistances: [], damage_vulnerabilities: [],
  };
  const targetTemplate = {
    name: "Target", armor_class: 17, max_hp: 100, speed_ft: 30, kind: "monster", size: "medium", traits: [],
    damage_immunities: [], damage_resistances: [], damage_vulnerabilities: [], critical_hit_minimum: 20,
  };
  const hero = { combatant_id: "hero-1", side: "heroes", position_ft: 5, state: window.IRON_PIT_BROWSER_STATE.buildState(fighterTemplate) };
  const target = { combatant_id: "monster-1", side: "monsters", position_ft: 10, state: window.IRON_PIT_BROWSER_STATE.buildState(targetTemplate) };
  hero.state.heroic_inspiration = true;
  const attack = { id: "greatsword", name: "Greatsword", kind: "melee", bonus: 9, diceCount: 2, diceSize: 6,
    damageBonus: 5, damageType: "slashing", reach: 5, animation: "heavy-slash" };
  setDice([5, 8, 3, 3]);
  const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(1, 1, hero, target, attack, 5, { spendAction: false });
  assert.equal(event.hit, true); assert.deepEqual(event.attack_roll.rolls, [8]); assert.equal(event.attack_roll.total, 17);
  assert.match(event.attack_roll.notation, /Heroic Inspiration/); assert.match(event.description, /Heroic Inspiration rerolls one d20/);
  assert.equal(hero.state.heroic_inspiration, false);
}

for (const htmlName of ["index.html", path.join("..", "index.html")]) {
  const html = fs.readFileSync(path.join(__dirname, htmlName), "utf8");
  assert.match(html, /browser-heroic-inspiration\.js/);
}

console.log("Browser Heroic Warrior / Heroic Inspiration parity regressions passed.");