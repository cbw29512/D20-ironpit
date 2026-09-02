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

const template = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];
assert.ok(template, "canonical Fighter must be exported");
assert.equal(template.fighting_style, "Defense");
assert.equal(template.armor_class, 17, "compiled Chain Mail + Defense AC must reach browser data");

const state = { template, active_modifiers: [] };
const M = window.IRON_PIT_BROWSER_MODIFIERS;
assert.equal(M.effectiveArmorClass(state), 17);

M.add(state, {
  id: "test:shield-of-faith",
  source_id: "cleric",
  source_effect_id: "shield-of-faith",
  kind: "armor-class",
  flat_bonus: 2,
});
assert.equal(M.effectiveArmorClass(state), 19, "temporary AC must stack after compiled Defense AC");

console.log("Browser Defense Fighting Style AC regressions passed.");
