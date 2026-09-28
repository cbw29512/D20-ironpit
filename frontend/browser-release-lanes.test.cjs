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
  assert.match(html, /<option value="2024" disabled>2024 — Coming Soon<\/option>/);
  assert.match(html, /D&amp;D 5e \(2014\) Beta combat simulator/);
}

const app = read("frontend/app.js");
assert.match(app, /const state = \{ ruleset: "2014"/);
assert.match(app, /if \(nextRuleset === "2024"\)/);
assert.match(app, /2024 is coming soon/);
assert.match(app, /await rulesetUi\(\)\.ensureBundle\(state\.ruleset\)/);

const rulesetUi = read("frontend/browser-ruleset-ui.js");
assert.match(rulesetUi, /SRD 5\.1 · BETA/);
assert.match(rulesetUi, /2024 — Coming Soon/);
assert.match(rulesetUi, /2014 Beta is live/);

console.log("Public release-lane labels and guards passed.");
