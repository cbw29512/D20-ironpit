"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

for (const file of [
  "browser-heroes.js", "browser-monsters-2014.js", "browser-condition-immunity.js", "browser-condition-rules.js",
  "browser-action-economy.js", "browser-grapple.js", "browser-modifier-validation.js", "browser-modifiers.js",
  "browser-state.js", "browser-rage.js", "browser-sneak-attack.js", "browser-rolls.js", "browser-undead-fortitude.js",
  "browser-terminal-effects.js", "browser-zero-hp.js", "browser-timed-conditions.js", "browser-weapon-mastery.js", "browser-ability-hooks.js",
  "browser-attack-outcome.js", "browser-attack.js", "browser-saving-throws.js", "browser-creature-kind.js", "browser-on-hit-condition-lifecycle.js", "browser-on-hit-condition-save.js",
  "browser-save-immunity.js", "browser-save-action-support.js", "browser-save-action-attempt.js", "browser-save-damage.js", "browser-save-damage-legacy.js", "browser-save-damage-apply.js", "browser-save-action-effects.js", "browser-save-event.js", "browser-saves.js", "browser-condition-lifecycle.js",
  "browser-hit-damage.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];

function dice(values) {
  const rolls = [...values];
  window.IRON_PIT_DICE = {
    roll(sides) { const value = rolls.shift(); if (!(value >= 1 && value <= sides)) throw new Error(`invalid d${sides}: ${value}`); return value; },
    rollMany(count, sides) { return Array.from({ length: count }, () => this.roll(sides)); },
  };
}

function member(id, options = {}) {
  const template = structuredClone(base);
  Object.assign(template, {
    id: `template-${id}`, name: id, armor_class: 10, max_hp: 40,
    saving_throw_bonuses: { constitution: 0 },
  });
  return { combatant_id: id, side: "monster", position_ft: 0, state: S.buildState(template) };
}

const compositeAttack = {
  id: "composite-poison", name: "Composite Poison", kind: "melee",
  bonus: 4, diceCount: 1, diceSize: 4, damageBonus: 3, damageType: "piercing",
  attackAbility: "strength", attackAbilityModifier: 3,
  onHitSaveDamage: {
    source: "Quasit-style Poison", saveAbility: "constitution", dc: 10,
    diceCount: 2, diceSize: 4, damageType: "poison", successDamage: "none",
    failedSaveCondition: {
      saveAbility: "constitution", dc: 10, conditionId: "poisoned",
      durationRounds: 10, repeatSaveTiming: "target_turn_end",
    },
  },
};

function runHit(saveRoll, poisonRolls = []) {
  dice([15, 4, saveRoll, ...poisonRolls]);
  const attacker = member("att");
  const target = member("tgt");
  const setup = { heroes: [], monsters: [attacker, target] };
  const result = window.IRON_PIT_BROWSER_ATTACK.resolve(
    1, 1, attacker, target, compositeAttack, 5, { setup, spendAction: false }
  );
  return { result, target };
}

const fail = runHit(5, [2, 2]);
assert.equal(fail.result.hit, true);
assert.equal(fail.result.saveSucceeded, false);
assert.ok(fail.result.damageComponents.some(c => c.source === "Quasit-style Poison" && c.applied_total === 4));
assert.ok(fail.result.appliedConditionIds.includes("poisoned") || fail.target.state.active_effect_ids.some(e => e.includes("poison")));

const success = runHit(15);
assert.equal(success.result.hit, true);
assert.equal(success.result.saveSucceeded, true);
assert.ok(!success.result.damageComponents.some(c => c.source === "Quasit-style Poison"));
assert.ok(!(success.result.appliedConditionIds || []).includes("poisoned"));

console.log("browser composite on-hit save parity passed");
