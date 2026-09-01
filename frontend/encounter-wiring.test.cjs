"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = __dirname;
const html = fs.readFileSync(path.join(root, "index.html"), "utf8");
const ids = new Set([...html.matchAll(/\bid="([^"]+)"/g)].map((match) => match[1]));

for (const file of ["app.js", "battlefield-picker.js", "battlefield-view.js", "battlefield-replay.js"]) {
  const source = fs.readFileSync(path.join(root, file), "utf8");
  const referenced = [
    ...source.matchAll(/\bel\("([^"]+)"\)/g),
    ...source.matchAll(/getElementById\("([^"]+)"\)/g),
  ].map((match) => match[1]);
  for (const id of referenced) assert.ok(ids.has(id), `${file} references missing #${id}`);
}

for (const id of [
  "hero-slots", "monster-slots", "fight-button", "pit-round", "status",
  "quick-test", "rerun-button", "reset-fight", "lab-summary",
  "card-picker", "picker-class", "picker-level", "picker-cr", "picker-monster",
  "confirm-card", "remove-card", "combat-fx-overlay",
]) assert.ok(ids.has(id), `battlefield is missing #${id}`);
assert.equal(ids.has("battle-seed"), false, "production battlefield must not expose a seeded RNG path");
assert.equal(ids.has("instant-mode"), false, "production battlefield must not expose a test-only instant path");
assert.equal(ids.has("picker-hero"), false, "canonical heroes must not expose a redundant build selector");
assert.equal(ids.has("distance"), false, "formation combat must not expose a starting-distance control");
assert.match(html, /<button id="quick-test" type="button">LOAD SAMPLE<\/button>/);
assert.match(html, /Production combat path · secure Web Crypto dice/);

const view = fs.readFileSync(path.join(root, "battlefield-view.js"), "utf8");
const replay = fs.readFileSync(path.join(root, "battlefield-replay.js"), "utf8");
const app = fs.readFileSync(path.join(root, "app.js"), "utf8");
const engine = fs.readFileSync(path.join(root, "browser-engine.js"), "utf8");
const formation = fs.readFileSync(path.join(root, "browser-formation.js"), "utf8");
const lab = fs.readFileSync(path.join(root, "battle-lab.js"), "utf8");
const dice = fs.readFileSync(path.join(root, "browser-dice.js"), "utf8");
const css = fs.readFileSync(path.join(root, "battlefield.css"), "utf8");

assert.match(view, /MAX_SLOTS = 6/); assert.match(app, /MAX_SLOTS = 6/);
assert.match(app, /Iron Pit ready\. Choose cards or load the sample matchup\./);
assert.doesNotMatch(app, /createSeededDice|battle-seed|instant-mode|IRON_PIT_DICE\s*=/);
assert.doesNotMatch(lab, /createSeededDice|seedNumber/);
assert.match(lab, /function diagnosticId/);
assert.match(dice, /crypto\.getRandomValues/); assert.match(dice, /function clearHistory/); assert.match(dice, /function getHistory/);
assert.match(engine, /1-6 cards per side/); assert.match(engine, /IRON_PIT_BROWSER_FORMATION/);
assert.match(formation, /HERO_FRONT = 5/); assert.match(formation, /MONSTER_FRONT = 10/);
assert.match(replay, /initiative-badge/); assert.match(replay, /critical-screen/); assert.match(replay, /fumble-blackout/);
assert.match(css, /\.battle-card\.turn-active/); assert.match(css, /card-turn-shake/); assert.match(css, /\.battle-card\.battle-dead/);
assert.ok(html.indexOf("browser-tactical-mind.js") < html.indexOf("browser-grapple.js"));
assert.ok(html.indexOf("browser-action-surge.js") < html.indexOf("browser-turn.js"));
assert.ok(html.indexOf("browser-formation.js") < html.indexOf("browser-engine.js"), "formation must load before the combat engine");
assert.ok(html.indexOf("battlefield-picker.js") < html.indexOf("app.js"));
assert.ok(html.indexOf("battlefield-view.js") < html.indexOf("app.js"));
assert.ok(html.indexOf("battlefield-replay.js") < html.indexOf("battle-lab.js"));
assert.ok(html.indexOf("battle-lab.js") < html.indexOf("app.js"));

console.log("production-path six-slot battlefield wiring regression passed");
