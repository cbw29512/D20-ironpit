"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const sizes = ["tiny", "small", "medium", "large", "huge", "gargantuan"];
let nextRoll = 5;
window.IRON_PIT_BROWSER_STATE = {
  sizeAtMost: (target, maximum) => sizes.indexOf(target.state.template.size) <= sizes.indexOf(maximum),
};
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = {
  immune: (state, conditionId) => state.template.condition_immunities.includes(conditionId),
};
window.IRON_PIT_BROWSER_ROLLS = {
  modeFromSources: () => "normal",
  d20: (bonus) => ({ rolls: [nextRoll], selected_roll: nextRoll, modifier: bonus, total: nextRoll + bonus, mode: "normal" }),
};
window.IRON_PIT_BROWSER_MODIFIERS = { applyD20Bonus: (_state, _kind, roll) => roll };
window.IRON_PIT_BROWSER_CONDITION_RULES = { autoFailStrDex: () => false };
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-saves.js"), "utf8"), { filename: "browser-saves.js" });

const attack = { onHitConditionSave: { saveAbility: "strength", dc: 13, conditionId: "prone", maxTargetSize: "large" } };
const target = (size = "medium", immunities = []) => ({ state: {
  template: { name: "Target", size, saving_throw_bonuses: { strength: 0 }, condition_immunities: immunities },
  active_effect_ids: [], is_dead: false, is_alive: true,
} });

nextRoll = 5;
const failed = target();
const failure = window.IRON_PIT_BROWSER_SAVES.resolveOnHitConditionSave(failed, attack);
assert.equal(failure.saveAbility, "strength");
assert.equal(failure.saveDc, 13);
assert.equal(failure.saveSucceeded, false);
assert.equal(failure.appliedCondition, "prone");
assert.ok(failed.state.active_effect_ids.includes("prone"));

nextRoll = 18;
const passed = target();
const success = window.IRON_PIT_BROWSER_SAVES.resolveOnHitConditionSave(passed, attack);
assert.equal(success.saveSucceeded, true);
assert.equal(success.appliedCondition, null);
assert.deepEqual(passed.state.active_effect_ids, []);

assert.equal(window.IRON_PIT_BROWSER_SAVES.resolveOnHitConditionSave(target("huge"), attack), null);
assert.equal(window.IRON_PIT_BROWSER_SAVES.resolveOnHitConditionSave(target("medium", ["prone"]), attack), null);
console.log("Browser on-hit condition saves match the universal failed-save condition policy.");