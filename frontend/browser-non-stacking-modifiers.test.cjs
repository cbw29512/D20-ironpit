"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = {};
window.IRON_PIT_BROWSER_EXHAUSTION = { effectiveSpeed: (_state, value) => value, d20Modifier: () => 0 };
window.IRON_PIT_BROWSER_DEBUFF_COUNTERS = { prevented: () => false };
vm.runInThisContext(fs.readFileSync("frontend/browser-modifiers.js", "utf8"));

const M = window.IRON_PIT_BROWSER_MODIFIERS;
const state = {
  template: { armor_class: 16, speed_ft: 30 },
  active_modifiers: [],
};

M.add(state, {
  id: "cover-a-ac", source_id: "a", source_effect_id: "half-cover-a",
  kind: "armor-class", flat_bonus: 2, non_stacking_group: "cover",
});
M.add(state, {
  id: "cover-b-ac", source_id: "b", source_effect_id: "half-cover-b",
  kind: "armor-class", flat_bonus: 2, non_stacking_group: "cover",
});
M.add(state, {
  id: "shield-ac", source_id: "c", source_effect_id: "shield-of-faith",
  kind: "armor-class", flat_bonus: 2,
});
assert.equal(M.effectiveArmorClass(state), 20);

M.add(state, {
  id: "cover-a-save", source_id: "a", source_effect_id: "half-cover-a",
  kind: "saving-throw-flat", flat_bonus: 2, save_ability: "dexterity",
  non_stacking_group: "cover",
});
M.add(state, {
  id: "cover-b-save", source_id: "b", source_effect_id: "half-cover-b",
  kind: "saving-throw-flat", flat_bonus: 2, save_ability: "dexterity",
  non_stacking_group: "cover",
});
assert.equal(M.savingThrowFlat(state, "dexterity"), 2);
state.active_modifiers = state.active_modifiers.filter((item) => item.source_id !== "a");
assert.equal(M.effectiveArmorClass(state), 20);
assert.equal(M.savingThrowFlat(state, "dexterity"), 2);
state.active_modifiers = state.active_modifiers.filter((item) => item.source_id !== "b");
assert.equal(M.effectiveArmorClass(state), 18);
assert.equal(M.savingThrowFlat(state, "dexterity"), 0);

console.log("Browser non-stacking modifier-group regressions passed.");
