"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

window.IRON_PIT_BROWSER_TIMED = {
  apply(state, id) {
    state.active_effect_ids ||= [];
    state.timed_effects ||= [];
    if (!state.active_effect_ids.includes(id)) state.active_effect_ids.push(id);
    if (!state.timed_effects.some((effect) => effect.effect_id === id)) {
      state.timed_effects.push({ effect_id: id });
    }
    return id;
  },
  removeEffect(state, effect) {
    state.timed_effects = state.timed_effects.filter((item) => item !== effect);
    if (!state.timed_effects.some((item) => item.effect_id === effect.effect_id)) {
      state.active_effect_ids = state.active_effect_ids.filter((id) => id !== effect.effect_id);
    }
  },
};
window.IRON_PIT_BROWSER_CONDITION_RULES = { incapacitated: () => false };
window.IRON_PIT_BROWSER_STATE = { effectiveMaxHp: (state) => state.template.max_hp };
window.IRON_PIT_BROWSER_WEAPON_MASTERY = {
  mastered: () => false,
  active: () => false,
};
window.IRON_PIT_BROWSER_ATTACK_OUTCOME = {
  requireOutcome: (ctx) => ctx.attackOutcome,
  noEventResult: (sequence) => ({ events: [], sequence, claimed: false }),
};
let recklessMarks = 0;
window.IRON_PIT_BROWSER_BARBARIAN3 = {
  markRecklessUse: () => { recklessMarks += 1; },
  bonusDamage: () => null,
};

load("browser-ability-hooks.js");
load("browser-attack-roll-context.js");
load("browser-barbarian2.js");
load("browser-tactical-master.js");
load("browser-brutal-strike.js");
load("browser-bloodied-fury.js");
load("browser-attack-roll-hook-installation.js");
window.IRON_PIT_DICE = {
  roll: () => 4,
  rollMany: (count) => Array.from({ length: count }, () => 4),
};
load("browser-rolls.js");

const H = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
const API = window.IRON_PIT_BROWSER_ATTACK_ROLL_CONTEXT;
assert.deepEqual(
  H.abilitiesFor(H.PHASES.BEFORE_ATTACK_ROLL).map((item) => item.id),
  ["reckless-attack", "sap-disadvantage", "brutal-strike", "bloodied-fury"],
);

function member(id, ruleset = "2024", extra = {}) {
  return {
    combatant_id: id,
    state: {
      active_effect_ids: [],
      timed_effects: [],
      feature_last_turn_keys: {},
      current_hp: 20,
      template: { id, name: id, ruleset, max_hp: 40, traits: [], ...extra },
    },
  };
}
const weapon = {
  id: "axe", kind: "melee", attackAbility: "strength",
  damageType: "slashing", isSpellAttack: false,
};
const spell = {
  id: "spell", kind: "melee", attackAbility: null,
  damageType: "force", isSpellAttack: true,
};

{
  const attacker = member("fighter");
  const target = member("reckless-target");
  target.state.active_effect_ids.push("reckless-attack");
  const roll = API.create();
  H.runPhase(H.PHASES.BEFORE_ATTACK_ROLL, {
    sequence: 1, round: 1, member: attacker, target, attack: spell,
    turnKey: "1:fighter", allowReckless: false,
    attackRollContext: roll, attackRollApi: API, events: [],
  });
  assert.equal(API.advantageSource(roll, "reckless-defender"), 1,
    "spell attacks must retain Advantage against a reckless defender");
}

{
  const attacker = member("barbarian", "2024", {
    reckless_attack: true, brutal_strike_damage_dice: 1,
  });
  const target = member("target");
  const roll = API.create();
  H.runPhase(H.PHASES.BEFORE_ATTACK_ROLL, {
    sequence: 7, round: 2, member: attacker, target, attack: weapon,
    turnKey: "2:barbarian", allowReckless: true,
    attackRollContext: roll, attackRollApi: API, events: [],
  });
  assert.equal(API.advantageSource(roll, "reckless-attacker"), 0,
    "Brutal Strike suppresses only the Reckless Attack Advantage source");
  assert.equal(roll.aggregateFeatureId, "reckless-attack");
  assert.match(roll.descriptionFragments.join(" "), /uses Reckless Attack/);
  assert.equal(recklessMarks, 1);
}

{
  const attacker = member("sapped-barbarian", "2024", {
    reckless_attack: true, brutal_strike_damage_dice: 1,
  });
  const target = member("target");
  window.IRON_PIT_BROWSER_TIMED.apply(attacker.state, "weapon-mastery-sap");
  const roll = API.create();
  H.runPhase(H.PHASES.BEFORE_ATTACK_ROLL, {
    sequence: 8, round: 2, member: attacker, target, attack: weapon,
    turnKey: "2:sapped-barbarian", allowReckless: true,
    attackRollContext: roll, attackRollApi: API, events: [],
  });
  assert.equal(API.disadvantageSource(roll, "sap"), 1);
  assert.equal(API.advantageSource(roll, "reckless-attacker"), 1,
    "Sap Disadvantage prevents Brutal Strike from suppressing Reckless Advantage");
  assert.equal(attacker.state.timed_effects.some((effect) => effect.effect_id === "weapon-mastery-sap"), false);
}

{
  const attacker = member("cancelled-disadvantage", "2024", {
    brutal_strike_damage_dice: 1,
  });
  attacker.state.active_effect_ids.push("reckless-attack");
  const damageAttack = {
    ...weapon, name: "Greataxe", diceCount: 1, diceSize: 12, damageBonus: 5,
    onHitDamage: [],
  };
  const rolled = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(
    attacker.state, damageAttack, false, "normal", "5:cancelled-disadvantage",
    null, null, false, true,
  );
  assert.equal(
    rolled.components.some((component) => component.source === "Brutal Strike"),
    false,
    "pre-roll Disadvantage must block Brutal Strike even when final mode is normal",
  );
}

{
  const attacker = member("boar", "2024", { traits: ["bloodied-fury"] });
  const target = member("target");
  const weaponRoll = API.create();
  H.runPhase(H.PHASES.BEFORE_ATTACK_ROLL, {
    sequence: 3, round: 1, member: attacker, target, attack: weapon,
    turnKey: "1:boar", allowReckless: false,
    attackRollContext: weaponRoll, attackRollApi: API, events: [],
  });
  assert.equal(API.advantageSource(weaponRoll, "bloodied-fury"), 1);

  const spellRoll = API.create();
  H.runPhase(H.PHASES.BEFORE_ATTACK_ROLL, {
    sequence: 4, round: 1, member: attacker, target, attack: spell,
    turnKey: "1:boar", allowReckless: false,
    attackRollContext: spellRoll, attackRollApi: API, events: [],
  });
  assert.equal(API.advantageSource(spellRoll, "bloodied-fury"), 0,
    "Bloodied Fury is weapon-only in the Python oracle");
}

for (const [file, forbidden] of [
  ["browser-attack.js", ["IRON_PIT_BROWSER_BRUTAL_STRIKE", "IRON_PIT_BROWSER_BARBARIAN2", "bloodiedFury", "SAP().disadvantage", "SAP().consume"]],
  ["browser-spell-attack.js", ["SAP().disadvantage", "SAP().consume"]],
]) {
  const source = fs.readFileSync(path.join(__dirname, file), "utf8");
  for (const token of forbidden) assert.equal(source.includes(token), false, `${file} still contains named pre-roll branch: ${token}`);
  assert.match(source, /PHASES\.BEFORE_ATTACK_ROLL/);
}

console.log("Browser beforeAttackRoll hook migration passed.");
