"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
const assertRuleset = (items, expected, label) => {
  assert.ok(items.length > 0, `${label} must not be empty`);
  for (const item of items) assert.equal(item.ruleset, expected, `${item.id} must carry explicit ${expected} ruleset identity`);
};

load("browser-heroes.js");
load("browser-monsters-generated.js");
assertRuleset(Object.values(window.IRON_PIT_BROWSER_HEROES), "2024", "canonical browser heroes");
assertRuleset(Object.values(window.IRON_PIT_BROWSER_MONSTERS), "2024", "canonical browser monsters");
for (const fixture of [
  "browser-monsters.js", "browser-monsters-fixed.js", "browser-monsters-beast2.js",
  "browser-monsters-batch3.js", "browser-monsters-control.js", "browser-monsters-expansion.js",
  "browser-monsters-venom.js", "browser-monsters-mixed.js", "browser-monsters-poison.js",
]) load(fixture);
assertRuleset(Object.values(window.IRON_PIT_BROWSER_MONSTERS), "2024", "legacy browser monster fixtures");

load("browser-monsters-2014.js");
const monsters2014 = Object.values(window.IRON_PIT_BROWSER_MONSTERS_2014);
assert.equal(monsters2014.length, 73, "2014 browser roster must contain exactly 73 certified monsters");
for (const id of [
  "2014-bandit", "2014-brown-bear", "2014-goblin", "2014-skeleton", "2014-fire-giant", "2014-owlbear",
  "2014-badger", "2014-cat", "2014-crab", "2014-hawk", "2014-lizard", "2014-rat", "2014-weasel",
  "2014-baboon", "2014-blood-hawk", "2014-giant-rat", "2014-ogre-zombie", "2014-raven", "2014-zombie",
  "2014-awakened-shrub", "2014-awakened-tree", "2014-giant-fire-beetle", "2014-giant-owl",
  "2014-kobold", "2014-owl", "2014-pteranodon", "2014-twig-blight",
  "2014-constrictor-snake", "2014-crocodile", "2014-flying-snake", "2014-giant-constrictor-snake",
  "2014-giant-crab", "2014-roc", "2014-tyrannosaurus-rex",
  "2014-ankylosaurus", "2014-dire-wolf", "2014-giant-crocodile", "2014-mastiff", "2014-wolf", "2014-worg",
]) {
  assert.ok(monsters2014.some((monster) => monster.id === id), `${id} must exist in the 2014 browser roster`);
}
assertRuleset(monsters2014, "2014", "2014 browser monsters");
assert.equal(window.IRON_PIT_2014_MVP_READY, true);
console.log("Browser combatants carry explicit isolated ruleset identity for 2014 and 2024.");