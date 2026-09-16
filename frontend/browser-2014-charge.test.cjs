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
    action_available: true, active_effect_ids: [], is_dead: false, is_unconscious: false,
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
window.IRON_PIT_BROWSER_ATTACK.resolveAttack = originalResolve;
assert.equal(result.handled, true);
assert.equal(observed.attack.onHitConditionSave.saveAbility, "strength");
assert.equal(observed.attack.onHitConditionSave.dc, 13);
assert.equal(observed.attack.onHitConditionSave.conditionId, "prone");
assert.equal(observed.options.proneMaxSize, undefined, "2014 save-based Charge must not use legacy direct Prone");

console.log("2014 declarative Charge browser parity passed.");
