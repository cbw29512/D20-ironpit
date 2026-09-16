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
load("browser-monsters-generated.js");

const heroes = Object.values(window.IRON_PIT_BROWSER_HEROES);
const monsters = Object.values(window.IRON_PIT_BROWSER_MONSTERS);
assert.ok(heroes.length > 0, "canonical browser heroes must be generated");
assert.ok(monsters.length > 0, "canonical browser monsters must be generated");
for (const hero of heroes) assert.equal(hero.ruleset, "2024", `${hero.id} must export explicit 2024 ruleset identity`);
for (const monster of monsters) assert.equal(monster.ruleset, "2024", `${monster.id} must export explicit 2024 ruleset identity`);

console.log("Generated browser combatants carry explicit 2024 ruleset identity.");
