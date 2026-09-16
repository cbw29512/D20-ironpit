"use strict";

const assert = require("node:assert/strict");

const roster = window.IRON_PIT_BROWSER_MONSTERS_2014;
const charge = (monsterId, attackId) => roster[monsterId].attacks.find((attack) => attack.id === attackId).charge;
const expected = [
  ["2014-elk", "2014-elk-ram", 20, 2, 6, "bludgeoning", "strength", 13],
  ["2014-giant-elk", "2014-giant-elk-ram", 20, 2, 6, "bludgeoning", "strength", 14],
  ["2014-giant-sea-horse", "2014-giant-sea-horse-ram", 20, 2, 6, "bludgeoning", "strength", 11],
  ["2014-minotaur-skeleton", "2014-minotaur-skeleton-gore", 10, 2, 8, "piercing", null, null],
  ["2014-rhinoceros", "2014-rhinoceros-gore", 20, 2, 8, "bludgeoning", "strength", 15],
];
for (const [monsterId, attackId, move, count, size, type, ability, dc] of expected) {
  const profile = charge(monsterId, attackId);
  assert.ok(profile, `${attackId} must serialize Charge`);
  assert.equal(profile.minimumMove, move);
  assert.equal(profile.diceCount, count);
  assert.equal(profile.diceSize, size);
  assert.equal(profile.damageType, type);
  assert.equal(profile.proneSaveAbility || null, ability);
  assert.equal(profile.proneSaveDc || null, dc);
}

for (const [monsterId, attackId, followUpId] of [
  ["2014-allosaurus", "2014-allosaurus-claw", "2014-allosaurus-bite"],
  ["2014-elephant", "2014-elephant-gore", "2014-elephant-stomp"],
  ["2014-mammoth", "2014-mammoth-gore", "2014-mammoth-stomp"],
  ["2014-panther", "2014-panther-claw", "2014-panther-bite"],
  ["2014-saber-toothed-tiger", "2014-saber-toothed-tiger-claw", "2014-saber-toothed-tiger-bite"],
  ["2014-tiger", "2014-tiger-claw", "2014-tiger-bite"],
  ["2014-triceratops", "2014-triceratops-gore", "2014-triceratops-stomp"],
  ["2014-warhorse", "2014-warhorse-hooves", "2014-warhorse-hooves"],
]) {
  const profile = charge(monsterId, attackId);
  assert.ok(profile, `${attackId} must serialize Charge`);
  assert.equal(profile.followUpAttackId, followUpId);
  assert.equal(profile.followUpRequiredTargetCondition, "prone");
  assert.equal(profile.followUpActionCost, "bonus_action");
}

const originalResolve = window.IRON_PIT_BROWSER_ATTACK.resolveAttack;
let observed = null;
window.IRON_PIT_BROWSER_ATTACK.resolveAttack = (sequence, round, member, target, attack, distance, options) => {
  observed = { attack, options };
  return { hit: false, target_id: target.combatant_id };
};
const elkAttack = roster["2014-elk"].attacks.find((attack) => attack.id === "2014-elk-ram");
const member = {
  side: "heroes", combatant_id: "elk",
  state: {
    action_available: true, bonus_action_available: true, active_effect_ids: [], is_dead: false, is_unconscious: false,
    initiative_total: 20, turn_terminated: false,
    template: { speed_ft: 50, attacks: [elkAttack] },
  },
};
const target = {
  side: "monsters", combatant_id: "target",
  state: {
    active_effect_ids: [], initiative_total: 10, is_alive: true, is_dead: false,
    is_unconscious: false, current_hp: 20, template: {},
  },
};
const result = window.IRON_PIT_BROWSER_CHARGE.resolveClosing(1, 1, member, target, { heroes: [member], monsters: [target] });
assert.equal(result.handled, true);
assert.equal(observed.attack.onHitConditionSave.saveAbility, "strength");
assert.equal(observed.attack.onHitConditionSave.dc, 13);
assert.equal(observed.attack.onHitConditionSave.conditionId, "prone");
assert.equal(observed.options.proneMaxSize, undefined, "2014 save-based Charge must not use legacy direct Prone");

function pouncePair() {
  const allosaurus = roster["2014-allosaurus"];
  const actor = {
    side: "heroes", combatant_id: "allosaurus",
    state: {
      action_available: true, bonus_action_available: true, active_effect_ids: [], is_dead: false, is_unconscious: false,
      initiative_total: 20, turn_terminated: false,
      template: { ...allosaurus, speed_ft: 60 },
    },
  };
  const defender = {
    side: "monsters", combatant_id: "prey",
    state: {
      active_effect_ids: [], initiative_total: 10, is_alive: true, is_dead: false,
      is_unconscious: false, current_hp: 100, template: { id: "prey" },
    },
  };
  return { actor, defender, setup: { heroes: [actor], monsters: [defender] } };
}

let pair = pouncePair();
let calls = [];
window.IRON_PIT_BROWSER_ATTACK.resolveAttack = (sequence, round, actor, defender, attack) => {
  calls.push(attack.id);
  return { hit: true, target_id: defender.combatant_id };
};
window.IRON_PIT_BROWSER_CHARGE.resolveClosing(1, 1, pair.actor, pair.defender, pair.setup);
assert.deepEqual(calls, ["2014-allosaurus-claw"], "Pounce Bite must not fire when the target is not Prone");
assert.equal(pair.actor.state.bonus_action_available, true, "failed Pounce follow-up must not spend Bonus Action");

pair = pouncePair();
calls = [];
window.IRON_PIT_BROWSER_ATTACK.resolveAttack = (sequence, round, actor, defender, attack) => {
  calls.push(attack.id);
  if (calls.length === 1) defender.state.active_effect_ids.push("prone");
  return { hit: true, target_id: defender.combatant_id };
};
window.IRON_PIT_BROWSER_CHARGE.resolveClosing(1, 1, pair.actor, pair.defender, pair.setup);
assert.deepEqual(calls, ["2014-allosaurus-claw", "2014-allosaurus-bite"]);
assert.equal(pair.actor.state.bonus_action_available, false, "legal Pounce follow-up must spend Bonus Action");

pair = pouncePair();
pair.defender.state.active_effect_ids.push("prone");
pair.actor.state.bonus_action_available = false;
calls = [];
window.IRON_PIT_BROWSER_ATTACK.resolveAttack = (sequence, round, actor, defender, attack) => {
  calls.push(attack.id);
  return { hit: true, target_id: defender.combatant_id };
};
window.IRON_PIT_BROWSER_CHARGE.resolveClosing(1, 1, pair.actor, pair.defender, pair.setup);
assert.deepEqual(calls, ["2014-allosaurus-claw"], "Pounce follow-up must require an available Bonus Action");

window.IRON_PIT_BROWSER_ATTACK.resolveAttack = originalResolve;
console.log("2014 declarative Charge and Pounce browser parity passed.");
