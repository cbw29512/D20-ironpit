"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = __dirname;
const html = fs.readFileSync(path.join(root, "index.html"), "utf8");
const ids = new Set([...html.matchAll(/\bid="([^"]+)"/g)].map((match) => match[1]));

for (const file of ["app.js", "encounter-view.js", "encounter-picker-view.js", "battle-replay.js"]) {
  const source = fs.readFileSync(path.join(root, file), "utf8");
  const referenced = [
    ...source.matchAll(/\bel\("([^"]+)"\)/g),
    ...source.matchAll(/getElementById\("([^"]+)"\)/g),
  ].map((match) => match[1]);
  for (const id of referenced) assert.ok(ids.has(id), `${file} references missing #${id}`);
}

for (const id of [
  "party-size", "hero-slot-pickers", "hero-cards", "monster-cr-filter",
  "monster-picker", "monster-picker-note", "add-monster", "monster-cards", "fight-button",
]) assert.ok(ids.has(id), `production picker is missing #${id}`);

const sizeOptions = [...html.matchAll(/<option value="([1-6])"[^>]*>[1-6]<\/option>/g)].map((match) => match[1]);
assert.deepEqual(sizeOptions, ["1", "2", "3", "4", "5", "6"]);
assert.ok(html.indexOf("encounter-picker.js") < html.indexOf("app.js"));
assert.ok(html.indexOf("encounter-picker-view.js") < html.indexOf("app.js"));
assert.ok(html.indexOf("encounter-view.js") < html.indexOf("app.js"));

console.log("encounter DOM wiring regression passed");
