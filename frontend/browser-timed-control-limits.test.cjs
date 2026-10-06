"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js",
  "browser-condition-rules.js",
  "browser-timed-conditions.js",
  "browser-timed-control-limits.js",
  "browser-action-economy.js",
  "browser-debuff-counters.js",
  "browser-modifier-validation.js",
  "browser-modifiers.js",
  "browser-exhaustion.js",
  "browser-state.js",
  "browser-rolls.js",
  "browser-saving-throws.js",
  "browser-ability-checks.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const T = window.IRON_PIT_BROWSER_TIMED;
const C = window.IRON_PIT_BROWSER_TIMED_CONTROL;
const E = window.IRON_PIT_ACTION_ECONOMY;
const M = window.IRON_PIT_BROWSER_MODIFIERS;
const SV = window.IRON_PIT_BROWSER_SAVING_THROWS;
const A = window.IRON_PIT_BROWSER_ABILITY_CHECKS;
const template = () => structuredClone(window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"]);
const member = () => ({ combatant_id: "hero", side: "heroes", position_ft: 0, state: S.buildState(template()) });

{
  const hero = member();
  const acBefore = M.effectiveArmorClass(hero.state);
  T.apply(hero.state, "slowed", "copper", {
    sourceEffectId: "slowing-breath",
    suppressReactions: true,
    controlLimits: {
      speed_multiplier: 0.5,
      action_bonus_exclusive: true,
      max_attacks_per_turn: 1,
      d20_disadvantage_abilities: [],
      armor_class_bonus: 0,
      saving_throw_flat_bonuses: [],
    },
  });
  S.beginTurn(hero.state);
  const expectedSpeed = Math.trunc((hero.state.template.speed_ft || 30) * 0.5);
  assert.equal(M.effectiveSpeed(hero.state), expectedSpeed);
  assert.equal(hero.state.movement_remaining_ft, expectedSpeed);
  assert.equal(E.available(hero.state, "reaction"), false);
  E.spend(hero.state, "action");
  assert.equal(E.available(hero.state, "bonus_action"), false);
  assert.equal(hero.state.movement_remaining_ft, expectedSpeed);
  assert.equal(M.effectiveArmorClass(hero.state), acBefore);
  assert.equal(M.savingThrowFlat(hero.state, "dexterity"), 0);
  assert.equal(C.abilityD20Disadvantage(hero.state, "strength"), 0);
  C.registerTurnAttack(hero.state, false);
  assert.equal(C.turnAttackAllowed(hero.state), false);
  C.registerTurnAttack(hero.state, true);
}

{
  const hero = member();
  T.apply(hero.state, "frightened", "paladin", {
    sourceEffectId: "abjure-foes",
    turnBehavior: "single_activity",
  });
  S.beginTurn(hero.state);
  E.spend(hero.state, "action");
  assert.equal(hero.state.movement_remaining_ft, 0);
  assert.equal(E.available(hero.state, "bonus_action"), false);
}

{
  const hero = member();
  const acBefore = M.effectiveArmorClass(hero.state);
  T.apply(hero.state, "weakened-strength", "gold", {
    sourceEffectId: "weakening-breath",
    controlLimits: {
      speed_multiplier: 1,
      action_bonus_exclusive: false,
      max_attacks_per_turn: null,
      d20_disadvantage_abilities: ["strength"],
      armor_class_bonus: 0,
      saving_throw_flat_bonuses: [],
    },
  });
  S.beginTurn(hero.state);
  assert.equal(M.effectiveSpeed(hero.state), hero.state.template.speed_ft || 30);
  assert.equal(E.available(hero.state, "reaction"), true);
  E.spend(hero.state, "action");
  assert.equal(E.available(hero.state, "bonus_action"), true);
  assert.equal(C.abilityD20Disadvantage(hero.state, "strength"), 1);
  assert.equal(C.abilityD20Disadvantage(hero.state, "dexterity"), 0);
  assert.equal(SV.saveMode(hero.state, "strength"), "disadvantage");
  assert.equal(SV.saveMode(hero.state, "dexterity"), "normal");
  assert.equal(A.mode(hero.state, 0, 0, { ability: "strength" }), "disadvantage");
  assert.equal(A.mode(hero.state, 0, 0, { ability: "dexterity" }), "normal");
  assert.equal(M.effectiveArmorClass(hero.state), acBefore);
  assert.equal(C.turnAttackAllowed(hero.state), true);
}

{
  const hero = member();
  const acBefore = M.effectiveArmorClass(hero.state);
  T.apply(hero.state, "slowed", "wizard", {
    sourceEffectId: "slow",
    suppressReactions: true,
    controlLimits: {
      speed_multiplier: 0.5,
      action_bonus_exclusive: true,
      max_attacks_per_turn: 1,
      d20_disadvantage_abilities: [],
      armor_class_bonus: -2,
      saving_throw_flat_bonuses: [{ ability: "dexterity", flat_bonus: -2 }],
    },
  });
  assert.equal(M.effectiveArmorClass(hero.state), acBefore - 2);
  assert.equal(M.savingThrowFlat(hero.state, "dexterity"), -2);
  assert.equal(M.savingThrowFlat(hero.state, "constitution"), 0);
}
