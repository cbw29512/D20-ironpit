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
const assertRuleset = (items, label) => {
  assert.ok(items.length > 0, `${label} must not be empty`);
  for (const item of items) {
    assert.equal(item.ruleset, "2024", `${item.id} must carry explicit 2024 ruleset identity`);
  }
};

load("browser-heroes.js");
load("browser-monsters-generated.js");
assertRuleset(Object.values(window.IRON_PIT_BROWSER_HEROES), "canonical browser heroes");
assertRuleset(Object.values(window.IRON_PIT_BROWSER_MONSTERS), "canonical browser monsters");

for (const fixture of [
  "browser-monsters.js",
  "browser-monsters-fixed.js",
  "browser-monsters-beast2.js",
  "browser-monsters-batch3.js",
  "browser-monsters-control.js",
  "browser-monsters-expansion.js",
  "browser-monsters-venom.js",
  "browser-monsters-mixed.js",
  "browser-monsters-poison.js",
]) load(fixture);
assertRuleset(Object.values(window.IRON_PIT_BROWSER_MONSTERS), "legacy browser monster fixtures");

console.log("Generated and legacy browser combatants carry explicit 2024 ruleset identity.");
