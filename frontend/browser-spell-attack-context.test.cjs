"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-grapple.js", "browser-timed-conditions.js", "browser-weapon-mastery.js", "browser-tactical-master.js",
  "browser-barbarian2.js", "browser-modifiers.js", "browser-state.js", "browser-rage.js", "browser-rolls.js",
  "browser-heroic-inspiration.js", "browser-undead-fortitude.js", "browser-zero-hp.js", "browser-attack.js",
  "browser-spellcasting.js", "browser-spell-modifiers.js", "browser-spell-attack.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const M = window.IRON_PIT_BROWSER_MODIFIERS;
const T = window.IRON_PIT_BROWSER_TIMED;
const X = window.IRON_PIT_BROWSER_SPELL_ATTACK;
const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];
const rangedSpell = {
  id: "test-spell-attack", name: "Test Spell Attack", level: 0, actionCost: "action", attackKind: "ranged", range: 120,
  attackBonus: 5, damageDiceCount: 1, damageDiceSize: 8, damageBonus: 0, damageType: "force",
  onHitModifierEffects: [], animation: "spell-attack",
};

function dice(values) {
  const rolls = [...values];
  window.IRON_PIT_DICE = {
    roll(sides) {
      if (!rolls.length) throw new Error("fixed dice exhausted");
      const value = rolls.shift();
      if (value < 1 || value > sides) throw new Error(`invalid d${sides}: ${value}`);
      return value;
    },
    rollMany(count, sides) { return Array.from({ length: count }, () => this.roll(sides)); },
  };
}

function member(id, side, position, armorClass = 10) {
  const template = structuredClone(base);
  template.id = `template-${id}`; template.name = id; template.armor_class = armorClass; template.resources = {};
  return { combatant_id: id, side, position_ft: position, state: S.buildState(template) };
}

function setup(distance = 30, targetAc = 10) {
  const caster = member("caster", "heroes", 0);
  const target = member("target", "monsters", distance, targetAc);
  return { caster, target, arena: { heroes: [caster], monsters: [target] } };
}

function study(caster, target) {
  M.add(caster.state, {
    id: "study-target", source_id: caster.combatant_id, source_effect_id: "studied-attacks",
    kind: "next-attack-against-advantage", flat_bonus: 0, dice_count: 0, dice_size: 0,
    damage_type: null, target_id: target.combatant_id, concentration_required: false,
    consume_on_attack_against: false, expires_source_turn_end_round: null,
  });
}

function sap(caster) {
  T.apply(caster.state, "weapon-mastery-sap", "enemy", {
    sourceEffectId: "weapon-mastery", appliedRound: 1, expiresRound: 2, expiryTiming: "source_turn_start",
  });
}

{
  const { caster, target, arena } = setup(30, 15); study(caster, target); dice([2, 15, 4]);
  const event = X.resolve(1, 1, caster, target, rangedSpell, arena, "1:caster");
  assert.equal(event.attack_roll.mode, "advantage"); assert.equal(event.hit, true);
  assert.equal(M.nextAttackAgainstAdvantage(caster.state, target.combatant_id), 0);
}

{
  const { caster, target, arena } = setup(30, 15); target.state.active_effect_ids.push("reckless-attack"); dice([2, 15, 4]);
  const event = X.resolve(1, 1, caster, target, rangedSpell, arena, "1:caster");
  assert.equal(event.attack_roll.mode, "advantage"); assert.equal(event.hit, true);
}

{
  const { caster, target, arena } = setup(30, 15); study(caster, target); sap(caster); dice([15, 4]);
  const event = X.resolve(1, 1, caster, target, rangedSpell, arena, "1:caster");
  assert.equal(event.attack_roll.mode, "normal"); assert.equal(event.hit, true);
  assert.equal(M.nextAttackAgainstAdvantage(caster.state, target.combatant_id), 0);
  assert.equal(caster.state.timed_effects.some((effect) => effect.effect_id === "weapon-mastery-sap"), false);
}

{
  const { caster, target, arena } = setup(30, 15); caster.state.heroic_inspiration = true; dice([2, 15, 4]);
  const event = X.resolve(1, 1, caster, target, rangedSpell, arena, "1:caster");
  assert.equal(event.hit, true); assert.equal(caster.state.heroic_inspiration, false);
  assert.match(event.description, /Heroic Inspiration rerolls one d20/);
}

{
  const { caster, target, arena } = setup(5, 15); dice([15, 4]);
  const meleeSpell = { ...rangedSpell, attackKind: "melee", range: 5 };
  const event = X.resolve(1, 1, caster, target, meleeSpell, arena, "1:caster");
  assert.equal(event.attack_roll.mode, "normal"); assert.equal(event.hit, true);
}

{
  const { caster, target, arena } = setup(5, 30); dice([18, 2]);
  const event = X.resolve(1, 1, caster, target, rangedSpell, arena, "1:caster");
  assert.equal(event.attack_roll.mode, "disadvantage"); assert.equal(event.attack_roll.selected_roll, 2);
}

console.log("Browser universal spell-attack context regressions passed.");
