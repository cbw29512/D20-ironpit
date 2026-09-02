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

const M = window.IRON_PIT_BROWSER_MODIFIERS;
const defenseState = { template, active_modifiers: [] };
assert.equal(M.effectiveArmorClass(defenseState), 17);
M.add(defenseState, {
  id: "test:shield-of-faith",
  source_id: "cleric",
  source_effect_id: "shield-of-faith",
  kind: "armor-class",
  flat_bonus: 2,
});
assert.equal(M.effectiveArmorClass(defenseState), 19, "temporary AC must stack after compiled Defense AC");

// Sword-and-shield content compiles Chain Mail 16 + Defense 1 + trained Shield 2 into base AC 19.
const shieldTemplate = structuredClone(template);
shieldTemplate.armor_class = 19;
shieldTemplate.visual = { ...shieldTemplate.visual, off_hand: "shield" };
const shieldState = { template: shieldTemplate, active_modifiers: [] };
assert.equal(M.effectiveArmorClass(shieldState), 19, "browser runtime must consume compiled shield AC exactly once");
M.add(shieldState, {
  id: "test:shield-of-faith-shield-build",
  source_id: "cleric",
  source_effect_id: "shield-of-faith",
  kind: "armor-class",
  flat_bonus: 2,
});
assert.equal(M.effectiveArmorClass(shieldState), 21, "temporary AC stacks after compiled shield AC");

console.log("Browser permanent equipment AC regressions passed.");
