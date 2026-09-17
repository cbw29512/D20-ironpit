"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const read = (file) => fs.readFileSync(path.join(__dirname, file), "utf8");

const frontend = read("index.html");
const root = read(path.join("..", "index.html"));
const modules = [
  "browser-turn-creature-effects.js",
  "browser-2014-paladin.js",
  "browser-2014-paladin-auras.js",
];

for (const moduleName of modules) {
  assert.ok(frontend.includes(moduleName), `frontend/index.html must load ${moduleName}`);
  assert.ok(root.includes(moduleName), `root index.html must load ${moduleName}`);
}

for (const page of [frontend, root]) {
  assert.ok(page.indexOf("browser-turn-creature-effects.js") < page.indexOf("browser-2014-paladin.js"));
  assert.ok(page.indexOf("browser-2014-paladin.js") < page.indexOf("browser-hit-damage.js"));
  assert.ok(page.indexOf("browser-2014-paladin-auras.js") < page.indexOf("browser-turn.js"));
}

console.log("Both Iron Pit entrypoints load the 2014 Paladin browser runtime in dependency order.");
