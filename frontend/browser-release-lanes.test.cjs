"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.join(__dirname, "..");
const read = (relative) => fs.readFileSync(path.join(root, relative), "utf8");

const origin = "https://ironpit.app";
const siteOrigin = read("frontend/site-origin.js");
assert.match(siteOrigin, /window\.IRON_PIT_SITE_URL = "https:\/\/ironpit\.app"/);
assert.match(siteOrigin, /planned domain/i);
assert.doesNotMatch(siteOrigin, /http:\/\//);
assert.equal([...siteOrigin.matchAll(/window\.IRON_PIT_SITE_URL =/g)].length, 1, "origin must be one assignment");

for (const page of ["index.html", "frontend/index.html"]) {
  const html = read(page);
  assert.match(html, /data-ruleset="2014"/);
  assert.match(html, /<option value="2014" selected>2014<\/option>/);
  assert.match(html, /<option value="2024">2024<\/option>/);
  assert.match(html, /combat-preset-recipes\.js/);
  assert.match(html, /A pocket dimension where heroes and monsters are drawn in to battle for the enjoyment of an audience/);
  assert.doesNotMatch(html, /Enter the Pit/);
  assert.match(html, /class="pit-chrome"/);
  assert.match(html, /How to use the Pit/);
  assert.ok(html.indexOf('id="pit"') < html.indexOf('id="how-heading"'), "arena must appear before marketing copy");
  assert.ok(html.indexOf("</main>") < html.indexOf('id="how-heading"'), "marketing copy must sit below the pit");
  assert.match(html, /The laws of the Pit/);
  assert.match(html, /Skip to the Pit/);
  assert.match(html, /<link rel="canonical" href="https:\/\/ironpit\.app\/">/);
  assert.match(html, /property="og:url" content="https:\/\/ironpit\.app\/"/);
  assert.match(html, /application\/ld\+json/);
  assert.match(html, /aria-live="polite"/);
  assert.match(html, /id="battle-log"[^>]*aria-label="Live battle log"/);
  assert.doesNotMatch(html, /Coming Soon/);
  assert.doesNotMatch(html, /Simulation note/);
  assert.doesNotMatch(html, /Light Tower/);
  assert.doesNotMatch(html, /Beta combat simulator/);
  assert.doesNotMatch(html, /netlify\.app/);
  assert.doesNotMatch(html.replace(/xmlns="http:\/\/www\.sitemaps\.org\/schemas\/sitemap\/0\.9"/g, ""), /http:\/\//);
}

for (const map of ["robots.txt", "frontend/robots.txt", "sitemap.xml", "frontend/sitemap.xml"]) {
  const text = read(map);
  assert.match(text, new RegExp(origin.replace(/[.]/g, "\\.")));
  assert.match(text, /planned/i);
}

const app = read("frontend/app.js");
assert.match(app, /const state = \{ ruleset: "2014"/);
assert.match(app, /await rulesetUi\(\)\.ensureBundle\(nextRuleset\)/);
assert.doesNotMatch(app, /2024 is coming soon/);

const rulesetUi = read("frontend/browser-ruleset-ui.js");
assert.match(rulesetUi, /D&D 5e 2014/);
assert.match(rulesetUi, /heroes · .* monsters ready for 2024 fights/);
assert.match(rulesetUi, /2014 is selected/);
assert.doesNotMatch(rulesetUi, /Coming Soon/);
assert.doesNotMatch(rulesetUi, /Beta/);

console.log("Public release-lane labels and guards passed.");
