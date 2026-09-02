"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const htmlPath of [path.join(__dirname, "index.html"), path.join(__dirname, "..", "index.html")]) {
  const html = fs.readFileSync(htmlPath, "utf8");
  assert.match(html, /browser-weapon-mastery\.js/, `${htmlPath} must load universal mastery rules`);
  assert.match(html, /browser-vex\.js/, `${htmlPath} must load shared Vex rules`);
  assert.ok(html.indexOf("browser-modifiers.js") < html.indexOf("browser-vex.js"));
  assert.ok(html.indexOf("browser-weapon-mastery.js") < html.indexOf("browser-vex.js"));
  assert.ok(html.indexOf("browser-vex.js") < html.indexOf("browser-attack.js"));
}
for (const file of [
  "browser-heroes.js", "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-grapple.js", "browser-modifiers.js", "browser-state.js", "browser-rage.js", "browser-sneak-attack.js",
  "browser-rolls.js", "browser-undead-fortitude.js", "browser-zero-hp.js", "browser-weapon-mastery.js",
  "browser-vex.js", "browser-attack.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE, M = window.IRON_PIT_BROWSER_MODIFIERS;
const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];
const vexAttack = {
  id: "mara-shortsword", weaponId: "shortsword", masteryProperty: "Vex", name: "Shortsword", kind: "melee",
  bonus: 5, diceCount: 1, diceSize: 6, damageBonus: 3, damageType: "piercing", reach: 5, animation: "thrust",
  sneakAttackEligible: true,
};

function dice(values) {
  const rolls = [...values];
  window.IRON_PIT_DICE = {
    roll(sides) { const value = rolls.shift(); if (!(value >= 1 && value <= sides)) throw new Error(`invalid d${sides}: ${value}`); return value; },
    rollMany(count, sides) { return Array.from({ length: count }, () => this.roll(sides)); },
  };
}
function member(id, side, options = {}) {
  const template = structuredClone(base);
  Object.assign(template, { id: `template-${id}`, name: id, armor_class: options.armorClass ?? 10,
    attacks: [structuredClone(vexAttack)], primary_attack_id: vexAttack.id, weapon_masteries: options.mastered === false ? [] : ["shortsword"],
    traits: [], sneak_attack_d6: options.sneakAttackD6 ?? 0, damage_immunities: options.immune ? ["piercing"] : [] });
  return { combatant_id: id, side, position_ft: options.position ?? 0, state: S.buildState(template) };
}
function attack(attacker, target, values, sequence = 1) {
  dice(values);
  return window.IRON_PIT_BROWSER_ATTACK.resolveAttack(sequence, 1, attacker, target, attacker.state.template.attacks[0], 5, { spendAction: false });
}

{
  const rogue = member("rogue", "heroes"), target = member("target", "monsters", { position: 5 });
  const first = attack(rogue, target, [15, 4]);
  assert.equal(first.hit, true); assert.match(first.description, /Vex primes/);
  assert.equal(M.nextAttackAgainstAdvantage(rogue.state, target.combatant_id), 1);
  target.state.template.armor_class = 30;
  const second = attack(rogue, target, [2, 3], 2);
  assert.equal(second.attack_roll.mode, "advantage"); assert.equal(second.hit, false);
  assert.equal(M.nextAttackAgainstAdvantage(rogue.state, target.combatant_id), 0, "the next roll consumes Vex even on a miss");
}

{
  const rogue = member("rogue", "heroes"), targetA = member("a", "monsters", { position: 5 }), targetB = member("b", "monsters", { position: 5 });
  attack(rogue, targetA, [15, 4]);
  const other = attack(rogue, targetB, [15, 4], 2);
  assert.equal(other.attack_roll.mode, "normal", "Vex is scoped to the creature that was damaged");
  assert.equal(M.nextAttackAgainstAdvantage(rogue.state, targetA.combatant_id), 1);
}

{
  const rogue = member("rogue", "heroes"), target = member("target", "monsters", { position: 5 });
  attack(rogue, target, [15, 4]);
  const chained = attack(rogue, target, [3, 18, 5], 2);
  assert.equal(chained.attack_roll.mode, "advantage"); assert.equal(chained.hit, true);
  assert.equal(M.nextAttackAgainstAdvantage(rogue.state, target.combatant_id), 1, "a damaging Vex hit refreshes the window");
}

{
  const rogue = member("rogue", "heroes", { sneakAttackD6: 1 }), target = member("target", "monsters", { position: 5 });
  attack(rogue, target, [15, 4]);
  const advantaged = attack(rogue, target, [3, 18, 5, 6], 2);
  assert.equal(advantaged.attack_roll.mode, "advantage");
  assert.equal(advantaged.damage_components[1].source, "Sneak Attack");
  assert.deepEqual(advantaged.damage_components[1].rolls, [6], "Vex Advantage enables the Rogue base-class Sneak Attack path");
}

{
  const rogue = member("rogue", "heroes"), immune = member("immune", "monsters", { position: 5, immune: true });
  const event = attack(rogue, immune, [15, 4]);
  assert.equal(event.damage_roll.total, 0);
  assert.equal(M.nextAttackAgainstAdvantage(rogue.state, immune.combatant_id), 0, "zero applied damage cannot trigger Vex");
}

{
  const rogue = member("rogue", "heroes", { mastered: false }), target = member("target", "monsters", { position: 5 });
  attack(rogue, target, [15, 4]);
  assert.equal(M.nextAttackAgainstAdvantage(rogue.state, target.combatant_id), 0, "unmastered Vex weapons do not activate mastery");
}

{
  const rogue = member("rogue", "heroes");
  window.IRON_PIT_BROWSER_VEX.apply(rogue.state, rogue.combatant_id, "target", vexAttack, 2, 1);
  assert.equal(M.expireSourceTurn([rogue.state], rogue.combatant_id, 2), 0);
  assert.equal(M.nextAttackAgainstAdvantage(rogue.state, "target"), 1);
  assert.equal(M.expireSourceTurn([rogue.state], rogue.combatant_id, 3), 1);
  assert.equal(M.nextAttackAgainstAdvantage(rogue.state, "target"), 0);
}

console.log("Browser Vex weapon mastery regressions passed.");
