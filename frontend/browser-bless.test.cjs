"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-grapple.js", "browser-modifiers.js", "browser-state.js", "browser-rage.js", "browser-rolls.js",
  "browser-undead-fortitude.js", "browser-zero-hp.js", "browser-attack.js", "browser-saves.js",
  "browser-concentration.js", "browser-spell-effects.js", "browser-spell-modifiers.js", "browser-precombat-spells.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const A = window.IRON_PIT_BROWSER_ATTACK;
const V = window.IRON_PIT_BROWSER_SAVES;
const C = window.IRON_PIT_BROWSER_CONCENTRATION;
const P = window.IRON_PIT_BROWSER_PRECOMBAT_SPELLS;
const bless = window.IRON_PIT_BROWSER_SPELL_EFFECTS.bless;
const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];

function dice(values) {
  const rolls = [...values];
  window.IRON_PIT_DICE = {
    roll: (sides) => {
      if (!rolls.length) throw new Error("fixed dice exhausted");
      const value = rolls.shift();
      if (value < 1 || value > sides) throw new Error(`invalid d${sides}: ${value}`);
      return value;
    },
    rollMany: (count, sides) => Array.from({ length: count }, () => window.IRON_PIT_DICE.roll(sides)),
  };
}

function member(id, side, position, kind = "melee", options = {}) {
  const template = structuredClone(base);
  template.id = `template-${id}`;
  template.name = id;
  const primary = template.attacks.find((attack) => attack.id === template.primary_attack_id) || template.attacks[0];
  primary.kind = kind;
  template.defensive_spell_actions = options.blessCaster ? [bless] : [];
  template.resources = options.blessCaster ? { "spell-slot-1": 1 } : {};
  if (options.armorClass != null) template.armor_class = options.armorClass;
  return { combatant_id: id, side, position_ft: position, state: S.buildState(template) };
}

function blessSetup() {
  const caster = member("caster", "heroes", 0, "ranged", { blessCaster: true });
  const frontFar = member("front-far", "heroes", 15);
  const backline = member("backline", "heroes", 10, "ranged");
  const frontNear = member("front-near", "heroes", 25);
  const outOfRange = member("out-of-range", "heroes", 35);
  const enemy = member("enemy", "monsters", 40, "melee", { armorClass: 30 });
  const setup = { heroes: [caster, frontFar, backline, frontNear, outOfRange], monsters: [enemy] };
  return { setup, caster, frontNear, frontFar, backline, outOfRange, enemy };
}

assert.equal(bless.level, 1);
assert.equal(bless.actionCost, "action");
assert.equal(bless.range, 30);
assert.equal(bless.durationMinutes, 1);
assert.equal(bless.targetPolicy, "friendly");
assert.equal(bless.targetCount, 3);
assert.deepEqual(bless.modifierEffects.map((effect) => effect.kind), ["attack-roll-bonus-die", "saving-throw-bonus-die"]);

{
  const { setup, caster, frontNear, frontFar, backline, outOfRange, enemy } = blessSetup();
  const selected = P.selectTargets(caster, setup, bless, 1);
  assert.deepEqual(selected.map((target) => target.combatant_id), ["front-near", "front-far", "caster"]);
  assert.ok(!selected.includes(backline));
  assert.ok(!selected.includes(outOfRange));

  const prep = P.prepare(setup);
  assert.equal(prep.events.length, 1);
  assert.equal(prep.events[0].feature_id, "bless");
  assert.equal(caster.state.resources["spell-slot-1"], 0);
  assert.equal(caster.state.concentration.effect_id, "bless");
  assert.equal(caster.state.concentration.expires_round, 11);

  for (const target of [frontNear, frontFar, caster]) {
    assert.deepEqual(new Set(target.state.active_modifiers.map((modifier) => modifier.kind)),
      new Set(["attack-roll-bonus-die", "saving-throw-bonus-die"]));
  }
  assert.equal(backline.state.active_modifiers.length, 0);
  assert.equal(outOfRange.state.active_modifiers.length, 0);

  const attack = frontNear.state.template.attacks.find((item) => item.id === frontNear.state.template.primary_attack_id);
  dice([10, 1]);
  const firstAttack = A.resolveAttack(2, 1, frontNear, enemy, attack, 5, { spendAction: false, setup });
  dice([10, 4]);
  const secondAttack = A.resolveAttack(3, 1, frontNear, enemy, attack, 5, { spendAction: false, setup });
  assert.equal(firstAttack.attack_roll.rolls.at(-1), 1);
  assert.equal(secondAttack.attack_roll.rolls.at(-1), 4);
  assert.match(firstAttack.attack_roll.notation, /1d4$/);
  assert.match(secondAttack.attack_roll.notation, /1d4$/);

  dice([10, 2]);
  const firstSave = V.resolveSavingThrow(caster.state, "constitution", 30);
  dice([10, 4]);
  const secondSave = V.resolveSavingThrow(caster.state, "constitution", 30);
  assert.equal(firstSave.roll.rolls.at(-1), 2);
  assert.equal(secondSave.roll.rolls.at(-1), 4);
  assert.match(firstSave.roll.notation, /1d4$/);
  assert.match(secondSave.roll.notation, /1d4$/);

  const states = [...setup.heroes, ...setup.monsters].map((entry) => entry.state);
  assert.equal(C.endIfExpired(caster.state, 10, states), false);
  assert.equal(C.endIfExpired(caster.state, 11, states), true);
  assert.equal(caster.state.concentration, null);
  assert.ok([frontNear, frontFar, caster].every((target) => target.state.active_modifiers.length === 0));
}

{
  const { setup, caster, frontNear, frontFar } = blessSetup();
  P.prepare(setup);
  const states = [...setup.heroes, ...setup.monsters].map((entry) => entry.state);
  dice([1, 1]);
  const check = C.resolveDamage(caster.state, 1, states);
  assert.equal(check.ended, true);
  assert.equal(caster.state.concentration, null);
  assert.ok([frontNear, frontFar, caster].every((target) => target.state.active_modifiers.length === 0));
}

console.log("Generated Bless targeting, independent-roll, and Concentration regressions passed.");
