"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
window.IRON_PIT_BROWSER_DEBUFF_COUNTERS = { prevented: () => false };
load("browser-modifiers.js");

const M = window.IRON_PIT_BROWSER_MODIFIERS;
const state = {
  template: { armor_class: 13, speed_ft: 30 },
  active_modifiers: [],
};
M.add(state, {
  id: "druid:barkskin:druid:0",
  source_id: "druid",
  source_effect_id: "barkskin",
  kind: "armor-class-minimum",
  minimum_value: 16,
});
assert.equal(M.effectiveArmorClass(state), 16);
state.template.armor_class = 18;
assert.equal(M.effectiveArmorClass(state), 18);
assert.throws(() => M.add(state, {
  id: "bad", source_id: "druid", source_effect_id: "bad",
  kind: "armor-class-minimum", minimum_value: 0,
}));

console.log("Browser minimum AC modifier parity passed.");
