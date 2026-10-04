"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.join(__dirname, "..");
const read = (relative) => fs.readFileSync(path.join(root, relative), "utf8");

for (const page of ["index.html", "frontend/index.html"]) {
  const html = read(page);
  assert.match(html, /data-ruleset="2014"/);
  assert.match(html, /<option value="2014" selected>2014 — Beta<\/option>/);
  assert.match(html, /<option value="2024">2024<\/option>/);
  assert.match(html, /combat-preset-recipes\.js/);
  assert.match(html, /D&amp;D 5e \(2014\) Beta combat simulator/);
  assert.doesNotMatch(html, /Coming Soon/);
}

const app = read("frontend/app.js");
assert.match(app, /const state = \{ ruleset: "2014"/);
assert.match(app, /await rulesetUi\(\)\.ensureBundle\(nextRuleset\)/);
assert.doesNotMatch(app, /2024 is coming soon/);

const rulesetUi = read("frontend/browser-ruleset-ui.js");
assert.match(rulesetUi, /SRD 5\.1 · BETA/);
assert.match(rulesetUi, /certified 2024 hero levels/);
assert.match(rulesetUi, /2014 Beta is live/);
assert.doesNotMatch(rulesetUi, /Coming Soon/);

console.log("Public release-lane labels and guards passed.");
