"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-modifiers.js",
  "browser-brutal-strike.js",
]) load(file);

const M = window.IRON_PIT_BROWSER_MODIFIERS;
const B = window.IRON_PIT_BROWSER_BRUTAL_STRIKE;

function state() {
  return { active_modifiers: [], template: { speed_ft: 30 }, current_hp: 10 };
}

{
  const target = state();
  assert.equal(B.staggering(target, "source"), true);
  assert.equal(target.active_modifiers.filter((item) => item.kind === "saving-throw-disadvantage").length, 1);
  assert.equal(target.active_modifiers.filter((item) => item.kind === "opportunity-attack-suppressed").length, 1);
  assert.equal(M.expireSourceTurnStart([target], "source"), 2);
  assert.equal(target.active_modifiers.length, 0);
}

{
  const target = state();
  assert.equal(B.sundering(target, "source"), true);
  assert.equal(M.nextIncomingAttackRollFlat(target, "source"), 0);
  assert.equal(M.nextIncomingAttackRollFlat(target, "ally"), 5);
  assert.equal(M.expireSourceTurnStart([target], "source"), 1);
  assert.equal(M.nextIncomingAttackRollFlat(target, "ally"), 0);
}

console.log("Browser advanced Brutal Strike effect regressions passed.");
