"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const htmlPath of [path.join(__dirname, "index.html"), path.join(__dirname, "..", "index.html")]) {
  const html = fs.readFileSync(htmlPath, "utf8");
  assert.match(html, /browser-studied-attacks\.js/, `${htmlPath} must load shared Studied Attacks rules`);
  assert.ok(html.indexOf("browser-modifiers.js") < html.indexOf("browser-studied-attacks.js"));
  assert.ok(html.indexOf("browser-studied-attacks.js") < html.indexOf("browser-attack.js"));
}
for (const file of [
  "browser-heroes.js", "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-grapple.js", "browser-modifiers.js", "browser-weapon-mastery.js", "browser-graze.js",
  "browser-studied-attacks.js", "browser-heroic-inspiration.js", "browser-state.js", "browser-rage.js",
  "browser-rolls.js", "browser-undead-fortitude.js", "browser-zero-hp.js", "browser-attack.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE, M = window.IRON_PIT_BROWSER_MODIFIERS;
const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l12"];

function dice(values) {
  const rolls = [...values];
  window.IRON_PIT_DICE = {
    roll(sides) { const value = rolls.shift(); if (!(value >= 1 && value <= sides)) throw new Error(`invalid d${sides}: ${value}`); return value; },
    rollMany(count, sides) { return Array.from({ length: count }, () => this.roll(sides)); },
  };
}
function member(id, side, options = {}) {
  const template = structuredClone(base);
  Object.assign(template, { id: `template-${id}`, name: id, armor_class: options.armorClass ?? 18,
    studied_attacks: options.studied !== false, traits: [] });
  return { combatant_id: id, side, position_ft: options.position ?? 0, state: S.buildState(template) };
}
function attack(attacker, target, values, sequence = 1) {
  dice(values);
  return window.IRON_PIT_BROWSER_ATTACK.resolveAttack(sequence, 1, attacker, target,
    attacker.state.template.attacks.find((item) => item.id === attacker.state.template.primary_attack_id), 5, { spendAction: false });
}

{
  const fighter = member("fighter", "heroes"), target = member("target", "monsters", { position: 5, armorClass: 30 });
  const first = attack(fighter, target, [2]);
  assert.equal(first.hit, false); assert.match(first.description, /Graze deals/); assert.match(first.description, /Studied Attacks primes/);
  assert.equal(M.nextAttackAgainstAdvantage(fighter.state, target.combatant_id), 1);
  target.state.template.armor_class = 18;
  const second = attack(fighter, target, [3, 18, 4, 4], 2);
  assert.equal(second.attack_roll.mode, "advantage"); assert.equal(second.hit, true);
  assert.equal(M.nextAttackAgainstAdvantage(fighter.state, target.combatant_id), 0);
}

{
  const fighter = member("fighter", "heroes"), a = member("a", "monsters", { position: 5, armorClass: 30 }), b = member("b", "monsters", { position: 5, armorClass: 10 });
  attack(fighter, a, [2]);
  const other = attack(fighter, b, [15, 4, 4], 2);
  assert.equal(other.attack_roll.mode, "normal");
  assert.equal(M.nextAttackAgainstAdvantage(fighter.state, a.combatant_id), 1, "study is target-scoped");
}

{
  const fighter = member("fighter", "heroes", { studied: false }), target = member("target", "monsters", { position: 5, armorClass: 30 });
  attack(fighter, target, [2]);
  assert.equal(M.nextAttackAgainstAdvantage(fighter.state, target.combatant_id), 0, "feature-absent combatants skip Studied Attacks");
}

{
  const fighter = member("fighter", "heroes"), target = member("target", "monsters", { position: 5, armorClass: 18 });
  fighter.state.heroic_inspiration = true;
  const event = attack(fighter, target, [2, 20, 4, 4]);
  assert.equal(event.hit, true); assert.match(event.description, /Heroic Inspiration rerolls/);
  assert.doesNotMatch(event.description, /Studied Attacks primes/);
  assert.equal(M.nextAttackAgainstAdvantage(fighter.state, target.combatant_id), 0);
}

{
  const fighter = member("fighter", "heroes");
  window.IRON_PIT_BROWSER_STUDIED_ATTACKS.apply(fighter.state, fighter.combatant_id, "target", 2);
  assert.equal(M.expireSourceTurn([fighter.state], fighter.combatant_id, 2), 0);
  assert.equal(M.nextAttackAgainstAdvantage(fighter.state, "target"), 1);
  assert.equal(M.expireSourceTurn([fighter.state], fighter.combatant_id, 3), 1);
}

console.log("Browser Studied Attacks regressions passed.");
