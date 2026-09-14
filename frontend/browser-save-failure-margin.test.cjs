const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = {
  IRON_PIT_DICE: { rollMany: (count, size) => { assert.equal(count, 1); assert.equal(size, 10); return [7]; } },
  IRON_PIT_BROWSER_CONDITION_IMMUNITY: { immune: () => false },
  IRON_PIT_BROWSER_TIMED: {
    apply: (state, conditionId, sourceId, options) => {
      state.active_effect_ids.push(conditionId);
      state.timed_effects.push({ effect_id: conditionId, source_id: sourceId, ...options });
      return conditionId;
    },
  },
};
vm.runInThisContext(fs.readFileSync(require.resolve("./browser-on-hit-save-conditions.js"), "utf8"), { filename: "browser-on-hit-save-conditions.js" });

const effect = {
  saveAbility: "constitution", dc: 10, conditionId: "poisoned", durationRounds: 10,
  failureMarginEscalation: {
    margin: 5, additionalConditionIds: ["unconscious"], replacementDurationDiceCount: 1,
    replacementDurationDiceSize: 10, replacementDurationRoundMultiplier: 10,
  },
};
const attack = { id: "bite" };
const target = () => ({ state: { is_alive: true, is_dead: false, active_effect_ids: [], timed_effects: [] } });

const nearMiss = target();
let result = window.IRON_PIT_BROWSER_ON_HIT_SAVE_CONDITIONS.applyFailure(nearMiss, attack, effect, { succeeded: false, roll: { total: 6 } }, "homunculus", 2);
assert.deepEqual(result.appliedConditions, ["poisoned"]);
assert.equal(nearMiss.state.timed_effects[0].expiresRound, 12);

const escalated = target();
result = window.IRON_PIT_BROWSER_ON_HIT_SAVE_CONDITIONS.applyFailure(escalated, attack, effect, { succeeded: false, roll: { total: 5 } }, "homunculus", 2);
assert.deepEqual(new Set(result.appliedConditions), new Set(["poisoned", "unconscious"]));
assert.deepEqual(new Set(escalated.state.timed_effects.map((item) => item.expiresRound)), new Set([72]));
console.log("Browser failed-save margin escalation regressions passed.");
