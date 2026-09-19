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
    if (!state.active_effect_ids.includes(id)) state.active_effect_ids.push(id);
    return id;
  },
};
window.IRON_PIT_BROWSER_CONDITION_RULES = { incapacitated: () => false };
window.IRON_PIT_BROWSER_STATE = { effectiveMaxHp: (state) => state.template.max_hp };
let recklessMarks = 0;
window.IRON_PIT_BROWSER_BARBARIAN3 = { markRecklessUse: () => { recklessMarks += 1; } };

load("browser-ability-hooks.js");
load("browser-attack-roll-context.js");
load("browser-barbarian2.js");
load("browser-brutal-strike.js");
load("browser-bloodied-fury.js");

const H = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
const API = window.IRON_PIT_BROWSER_ATTACK_ROLL_CONTEXT;
assert.deepEqual(
  H.abilitiesFor(H.PHASES.BEFORE_ATTACK_ROLL).map((item) => item.id),
  ["reckless-attack", "brutal-strike", "bloodied-fury"],
);

function member(id, ruleset = "2024", extra = {}) {
  return {
    combatant_id: id,
    state: {
      active_effect_ids: [],
      feature_last_turn_keys: {},
      current_hp: 20,
      template: { id, name: id, ruleset, max_hp: 40, traits: [], ...extra },
    },
  };
}
const strengthMelee = { id: "axe", kind: "melee", attackAbility: "strength", damageType: "slashing" };

{
  const attacker = member("fighter");
  const target = member("reckless-target");
  target.state.active_effect_ids.push("reckless-attack");
  const roll = API.create();
  H.runPhase(H.PHASES.BEFORE_ATTACK_ROLL, {
    sequence: 1, round: 1, member: attacker, target, attack: strengthMelee,
    turnKey: "1:fighter", allowReckless: false, attackRollContext: roll, attackRollApi: API, events: [],
  });
  assert.equal(API.advantageSource(roll, "reckless-defender"), 1,
    "non-Barbarians must retain Advantage against a reckless defender");
}

{
  const attacker = member("barbarian", "2024", {
    reckless_attack: true, brutal_strike_damage_dice: 1,
  });
  const target = member("target");
  const roll = API.create();
  const result = H.runPhase(H.PHASES.BEFORE_ATTACK_ROLL, {
    sequence: 7, round: 2, member: attacker, target, attack: strengthMelee,
    turnKey: "2:barbarian", allowReckless: true, attackRollContext: roll, attackRollApi: API, events: [],
  });
  assert.equal(result.sequence, 7);
  assert.deepEqual(result.events, []);
  assert.equal(API.advantageSource(roll, "reckless-attacker"), 0,
    "Brutal Strike suppresses only the Reckless Attack Advantage source");
  assert.equal(roll.aggregateFeatureId, "reckless-attack");
  assert.match(roll.descriptionFragments.join(" "), /uses Reckless Attack/);
  assert.equal(recklessMarks, 1);
}

{
  const attacker = member("boar", "2024", { traits: ["bloodied-fury"] });
  attacker.state.current_hp = 20;
  const target = member("target");
  const roll = API.create();
  H.runPhase(H.PHASES.BEFORE_ATTACK_ROLL, {
    sequence: 3, round: 1, member: attacker, target, attack: strengthMelee,
    turnKey: "1:boar", allowReckless: false, attackRollContext: roll, attackRollApi: API, events: [],
  });
  assert.equal(API.advantageSource(roll, "bloodied-fury"), 1);
}

const attackSource = fs.readFileSync(path.join(__dirname, "browser-attack.js"), "utf8");
for (const forbidden of ["IRON_PIT_BROWSER_BRUTAL_STRIKE", "IRON_PIT_BROWSER_BARBARIAN2", "bloodiedFury"]) {
  assert.equal(attackSource.includes(forbidden), false, `named pre-roll branch remains: ${forbidden}`);
}
assert.match(attackSource, /PHASES\.BEFORE_ATTACK_ROLL/);

console.log("Browser beforeAttackRoll hook migration passed.");
