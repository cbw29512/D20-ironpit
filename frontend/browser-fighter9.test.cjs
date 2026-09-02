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

window.IRON_PIT_BROWSER_STATE = {
  canProne: () => false,
  sizeAtMost: () => false,
  distance: (a, b) => Math.abs(a.position_ft - b.position_ft),
};
window.IRON_PIT_BROWSER_GRAPPLE = {
  attackDisadvantage: () => 0,
  speedIsZero: () => false,
  apply: () => [],
};
window.IRON_PIT_BROWSER_CONDITION_RULES = {
  has: (state, id) => state.active_effect_ids.includes(id),
  attackAdvantage: () => false,
  autoCritical: () => false,
  incapacitated: (state) => state.is_unconscious,
  autoFailStrDex: () => false,
};
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_BARBARIAN2 = {
  activate: () => false,
  attackAdvantage: () => 0,
  attacksAgainstAdvantage: () => 0,
  dangerSenseAdvantage: () => 0,
};
window.IRON_PIT_BROWSER_RAGE = { damageBonus: () => 0, extendFromAttack: () => {}, endIfIncapacitated: () => {} };
window.IRON_PIT_BROWSER_CHAMPION = { criticalMove: (_attacker, _setup, event) => event };
window.IRON_PIT_BROWSER_CONCENTRATION = { endIfIncapacitated: () => {} };
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "reaction" ? state.reaction_available : cost === "bonus_action" ? state.bonus_action_available : state.action_available,
  spend: (state, cost) => {
    if (cost === "reaction") state.reaction_available = false;
    else if (cost === "bonus_action") state.bonus_action_available = false;
    else state.action_available = false;
  },
};
window.IRON_PIT_BROWSER_ZERO_HP = {
  applyDamage: (state, amount) => {
    state.current_hp = Math.max(0, state.current_hp - amount);
    if (state.current_hp === 0) state.is_unconscious = true;
    return null;
  },
};

load("browser-rolls.js");
load("browser-timed-conditions.js");
load("browser-weapon-mastery.js");
load("browser-tactical-master.js");
load("browser-graze.js");
load("browser-modifiers.js");
load("browser-attack.js");
load("browser-saves.js");
load("browser-indomitable.js");

const greatsword = {
  id: "karnok-greatsword", weaponId: "greatsword", name: "Greatsword", kind: "melee", bonus: 9,
  diceCount: 2, diceSize: 6, damageBonus: 5, damageType: "slashing", reach: 5, animation: "heavy-slash",
  damageDieMinimum: 3, masteryProperty: "Graze", attackAbilityModifier: 5,
};
const shortbow = {
  id: "karnok-shortbow", weaponId: "shortbow", name: "Shortbow", kind: "ranged", bonus: 5,
  diceCount: 1, diceSize: 6, damageBonus: 1, damageType: "piercing", normal: 80, long: 320,
  reach: 5, animation: "projectile", masteryProperty: "Vex", attackAbilityModifier: 1,
};
const fighterTemplate = {
  name: "Karnok Stoneward", kind: "character", armor_class: 17, max_hp: 94, speed_ft: 30, size: "medium",
  traits: [], damage_immunities: [], damage_resistances: [], damage_vulnerabilities: [],
  critical_hit_minimum: 19, tactical_master_sap_weapon_ids: ["greatsword"], indomitable_bonus: 9,
  weapon_masteries: ["flail", "javelin", "spear", "greatsword"],
  saving_throw_bonuses: { strength: 9, dexterity: 1, constitution: 8, intelligence: 0, wisdom: 0, charisma: 0 },
};
const targetTemplate = {
  name: "Target", kind: "monster", armor_class: 17, max_hp: 100, speed_ft: 30, size: "medium",
  traits: [], damage_immunities: [], damage_resistances: [], damage_vulnerabilities: [],
  critical_hit_minimum: 20, tactical_master_sap_weapon_ids: [], weapon_masteries: [],
  saving_throw_bonuses: { strength: 2, dexterity: 2, constitution: 2, intelligence: 0, wisdom: 0, charisma: 0 },
};

function state(template, resources = {}) {
  return {
    template, current_hp: template.max_hp, temporary_hp: 0, is_alive: true, is_dead: false,
    is_unconscious: false, is_stable: false, death_save_successes: 0, death_save_failures: 0,
    action_available: true, bonus_action_available: true, reaction_available: true, movement_remaining_ft: 30,
    active_effect_ids: [], grapple_sources: [], timed_effects: [], active_modifiers: [],
    temporary_damage_resistances: [], resources: { ...resources }, feature_last_turn_keys: {},
  };
}

{
  const hero = { combatant_id: "hero-1", side: "heroes", position_ft: 5, state: state(fighterTemplate, { indomitable: 1 }) };
  const target = { combatant_id: "monster-1", side: "monsters", position_ft: 10, state: state(targetTemplate) };
  const setup = { heroes: [hero], monsters: [target] };
  assert.equal(window.IRON_PIT_BROWSER_TACTICAL_MASTER.selected(hero.state, greatsword), true);
  assert.equal(window.IRON_PIT_BROWSER_WEAPON_MASTERY.active(hero.state, greatsword, "Graze"), false);
  setDice([10, 3, 3]);
  const hit = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(1, 1, hero, target, greatsword, 5, { setup, spendAction: false });
  assert.equal(hit.hit, true);
  assert.match(hit.description, /Tactical Master applies Sap/);
  assert.equal(target.state.timed_effects.some((effect) => effect.effect_id === "tactical-master-sap"), true);

  setDice([18, 2]);
  const reply = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(2, 1, target, hero, {
    ...greatsword, id: "target-sword", weaponId: "longsword", bonus: 5, damageDieMinimum: undefined, masteryProperty: undefined,
  }, 5, { setup, spendAction: false });
  assert.equal(reply.attack_roll.mode, "disadvantage");
  assert.deepEqual(reply.attack_roll.rolls, [18, 2]);
  assert.equal(target.state.timed_effects.some((effect) => effect.effect_id === "tactical-master-sap"), false);

  const missHero = { combatant_id: "hero-miss", side: "heroes", position_ft: 5, state: state(fighterTemplate) };
  const missTarget = { combatant_id: "monster-miss", side: "monsters", position_ft: 10, state: state(targetTemplate) };
  const hpBefore = missTarget.state.current_hp;
  setDice([1]);
  const miss = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(3, 2, missHero, missTarget, greatsword, 5, { spendAction: false });
  assert.equal(miss.hit, false);
  assert.equal(miss.damage_roll, null);
  assert.equal(missTarget.state.current_hp, hpBefore);
}

{
  const sapTemplate = { ...fighterTemplate, name: "Sap Master", tactical_master_sap_weapon_ids: [], weapon_masteries: ["longsword"] };
  const sapSword = {
    id: "sap-longsword", weaponId: "longsword", name: "Longsword", kind: "melee", bonus: 9,
    diceCount: 1, diceSize: 8, damageBonus: 4, damageType: "slashing", reach: 5, masteryProperty: "Sap",
  };
  const hero = { combatant_id: "hero-sap", side: "heroes", position_ft: 5, state: state(sapTemplate) };
  const target = { combatant_id: "monster-sap", side: "monsters", position_ft: 10, state: state(targetTemplate) };
  const setup = { heroes: [hero], monsters: [target] };
  assert.equal(window.IRON_PIT_BROWSER_SAP.weaponEligible(hero.state, sapSword), true);
  setDice([10, 4]);
  const hit = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(4, 1, hero, target, sapSword, 5, { setup, spendAction: false });
  assert.equal(hit.hit, true);
  assert.match(hit.description, /Sap mastery affects Target/);
  assert.doesNotMatch(hit.description, /Tactical Master applies Sap/);
  assert.equal(target.state.timed_effects.some((effect) => effect.effect_id === "weapon-mastery-sap"), true);

  setDice([18, 2]);
  const reply = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(5, 1, target, hero, {
    ...sapSword, id: "reply-sword", weaponId: "unmastered-longsword", bonus: 5, masteryProperty: undefined,
  }, 5, { setup, spendAction: false });
  assert.equal(reply.attack_roll.mode, "disadvantage");
  assert.deepEqual(reply.attack_roll.rolls, [18, 2]);
  assert.equal(target.state.timed_effects.some((effect) => effect.effect_id === "weapon-mastery-sap"), false);
}

{
  const failedState = state(fighterTemplate, { indomitable: 1 });
  assert.equal(window.IRON_PIT_BROWSER_TACTICAL_MASTER.eligible(failedState, greatsword), true);
  assert.equal(window.IRON_PIT_BROWSER_TACTICAL_MASTER.eligible(failedState, shortbow), false);
  setDice([2, 10]);
  const failedThenRerolled = window.IRON_PIT_BROWSER_SAVES.resolveSavingThrow(failedState, "wisdom", 15);
  assert.equal(failedThenRerolled.succeeded, true);
  assert.equal(failedThenRerolled.roll.selected_roll, 10);
  assert.equal(failedThenRerolled.roll.total, 19);
  assert.match(failedThenRerolled.roll.notation, /Indomitable \+9/);
  assert.equal(failedState.resources.indomitable, 0);

  const successState = state(fighterTemplate, { indomitable: 1 });
  setDice([15]);
  const success = window.IRON_PIT_BROWSER_SAVES.resolveSavingThrow(successState, "wisdom", 15);
  assert.equal(success.succeeded, true);
  assert.equal(success.roll.total, 15);
  assert.equal(successState.resources.indomitable, 1);
}

for (const htmlName of ["index.html", path.join("..", "index.html")]) {
  const html = fs.readFileSync(path.join(__dirname, htmlName), "utf8");
  assert.match(html, /browser-weapon-mastery\.js/);
  assert.match(html, /browser-tactical-master\.js/);
  assert.match(html, /browser-indomitable\.js/);
}

console.log("Browser Fighter 9 Tactical Master replacement and automatic Indomitable regressions passed.");
