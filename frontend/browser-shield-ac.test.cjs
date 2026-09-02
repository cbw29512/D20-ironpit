"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

load("browser-heroes.js");
load("browser-modifiers.js");

const canonical = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];
assert.ok(canonical, "canonical Fighter must be exported");

// A sword-and-shield Fighter compiles Chain Mail 16 + Defense 1 + Shield 2 into base AC 19.
const template = structuredClone(canonical);
template.armor_class = 19;
template.visual = { ...template.visual, off_hand: "shield" };
const state = { template, active_modifiers: [] };
const M = window.IRON_PIT_BROWSER_MODIFIERS;

assert.equal(M.effectiveArmorClass(state), 19, "browser runtime must consume compiled shield AC exactly once");
M.add(state, {
  id: "test:shield-of-faith",
  source_id: "cleric",
  source_effect_id: "shield-of-faith",
  kind: "armor-class",
  flat_bonus: 2,
});
assert.equal(M.effectiveArmorClass(state), 21, "temporary AC modifiers stack after compiled shield AC");

console.log("Browser Shield AC regressions passed.");
