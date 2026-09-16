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
const assertRuleset = (items, expected, label) => {
  assert.ok(items.length > 0, `${label} must not be empty`);
  for (const item of items) {
    assert.equal(item.ruleset, expected, `${item.id} must carry explicit ${expected} ruleset identity`);
  }
};

load("browser-heroes.js");
load("browser-monsters-generated.js");
assertRuleset(Object.values(window.IRON_PIT_BROWSER_HEROES), "2024", "canonical browser heroes");
assertRuleset(Object.values(window.IRON_PIT_BROWSER_MONSTERS), "2024", "canonical browser monsters");

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
assertRuleset(Object.values(window.IRON_PIT_BROWSER_MONSTERS), "2024", "legacy browser monster fixtures");

load("browser-monsters-2014.js");
const monsters2014 = Object.values(window.IRON_PIT_BROWSER_MONSTERS_2014);
assert.equal(monsters2014.length, 4, "2014 MVP browser roster must contain exactly four certified monsters");
assert.deepEqual(
  monsters2014.map((monster) => monster.id).sort(),
  ["2014-bandit", "2014-brown-bear", "2014-goblin", "2014-skeleton"],
  "2014 browser test lane must expose only the certified MVP identities",
);
assertRuleset(monsters2014, "2014", "2014 MVP browser monsters");
assert.equal(window.IRON_PIT_2014_MVP_READY, true);

console.log("Browser combatants carry explicit isolated ruleset identity for 2014 and 2024.");