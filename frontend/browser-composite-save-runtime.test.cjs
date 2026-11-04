global.window = global.window || {};
const assert = require("node:assert/strict");
const path = require("node:path");
require(path.join(__dirname, "browser-on-hit-condition-save.js"));
require(path.join(__dirname, "browser-hit-damage.js"));

let saveCalls = 0;
window.IRON_PIT_BROWSER_SAVING_THROWS = {
  resolveSavingThrow: () => { saveCalls += 1; return { roll: { total: 5 }, succeeded: false }; },
};
window.IRON_PIT_DICE = { rollMany: (c, s) => Array(c).fill(2) };
window.IRON_PIT_BROWSER_SAVES = {
  resolveSavingThrow: (...a) => window.IRON_PIT_BROWSER_SAVING_THROWS.resolveSavingThrow(...a),
  resolveOnHitConditionSave: (target, attack, src, round, setup, attacker, shared) => {
    if (shared) assert.equal(shared.succeeded, false);
    return window.IRON_PIT_BROWSER_ON_HIT_CONDITION_SAVE.resolve(target, attack, src, round, setup, attacker, shared);
  },
};
window.IRON_PIT_BROWSER_TIMED = { apply: (state, id) => { state.active_effect_ids.push(id); return id; } };
window.IRON_PIT_BROWSER_STATE = { sizeAtMost: () => true };
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_CREATURE_KIND = { matches: () => false };
window.IRON_PIT_BROWSER_ON_HIT_CONDITION_LIFECYCLE = { attachStartTurnDamage: () => {} };

const attack = {
  id: "composite", name: "Composite",
  onHitSaveDamage: {
    source: "poison", saveAbility: "constitution", dc: 10,
    diceCount: 2, diceSize: 4, damageType: "poison", successDamage: "none",
    failedSaveCondition: {
      saveAbility: "constitution", dc: 10, conditionId: "poisoned",
      durationRounds: 10, repeatSaveTiming: "target_turn_end",
    },
  },
};
const target = { state: { is_alive: true, is_dead: false, active_effect_ids: [], timed_effects: [] }, combatant_id: "t" };
const damage = window.IRON_PIT_BROWSER_HIT_DAMAGE.resolveSaveDamage(target.state, attack);
assert.equal(damage.saveSucceeded, false);
assert.equal(saveCalls, 1, "damage save rolls once");
const condition = window.IRON_PIT_BROWSER_SAVES.resolveOnHitConditionSave(
  target, { ...attack, onHitConditionSave: attack.onHitSaveDamage.failedSaveCondition },
  null, 1, null, null, { roll: damage.saveRoll, succeeded: damage.saveSucceeded },
);
assert.equal(condition.appliedCondition, "poisoned");
assert.equal(saveCalls, 1, "condition reuses shared save, no second roll");
console.log("browser composite save parity locked");
