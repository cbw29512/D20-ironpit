"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = __dirname;
const html = fs.readFileSync(path.join(root, "index.html"), "utf8");
const ids = new Set([...html.matchAll(/\bid="([^"]+)"/g)].map((match) => match[1]));

for (const file of ["app.js", "battle-actions.js", "battlefield-picker.js", "battlefield-view.js", "battlefield-replay.js", "turbo-view.js"]) {
  const source = fs.readFileSync(path.join(root, file), "utf8");
  const referenced = [
    ...source.matchAll(/\bel\("([^"]+)"\)/g),
    ...source.matchAll(/getElementById\("([^"]+)"\)/g),
  ].map((match) => match[1]);
  for (const id of referenced) assert.ok(ids.has(id), `${file} references missing #${id}`);
}

for (const id of [
  "hero-slots", "monster-slots", "fight-button", "step-fight-button", "pit-round", "status",
  "step-session-actions", "next-event-button", "watch-rest-button",
  "quick-test", "rerun-button", "reset-fight", "lab-summary",
  "turbo-count", "turbo-button", "turbo-panel", "turbo-result-title", "turbo-result-summary",
  "turbo-heroes", "turbo-monsters", "turbo-draws", "turbo-rounds", "turbo-notables",
  "turbo-fight-number", "turbo-replay-button", "turbo-replay-step-button", "turbo-error-summary",
  "card-picker", "picker-class", "picker-level", "picker-cr", "picker-monster",
  "confirm-card", "remove-card", "combat-fx-overlay",
]) assert.ok(ids.has(id), `battlefield is missing #${id}`);
assert.equal(ids.has("battle-seed"), false, "production battlefield must not expose a seeded RNG path");
assert.equal(ids.has("instant-mode"), false, "production battlefield must not expose a test-only instant path");
assert.equal(ids.has("picker-hero"), false, "canonical heroes must not expose a redundant build selector");
assert.equal(ids.has("distance"), false, "formation combat must not expose a starting-distance control");
assert.match(html, /<button id="quick-test" type="button">LOAD SAMPLE<\/button>/);
assert.match(html, /id="step-fight-button"/); assert.match(html, /id="turbo-count"[^>]+value="100"/);
assert.match(html, /browser-turbo\.js/); assert.match(html, /browser-execution\.js/); assert.match(html, /battle-actions\.js/);
assert.match(html, /browser-arena-map\.js/); assert.match(html, /browser-grid-geometry\.js/);
assert.match(html, /browser-grid-movement\.js/); assert.match(html, /browser-grid-placement\.js/);
assert.match(html, /combatant-art\.js/);
assert.match(html, /Production combat path · secure Web Crypto dice/);
assert.match(html, /browser-offense-value\.js/); assert.match(html, /browser-spell-offense\.js/);

const view = fs.readFileSync(path.join(root, "battlefield-view.js"), "utf8");
const replay = fs.readFileSync(path.join(root, "battlefield-replay.js"), "utf8");
const app = fs.readFileSync(path.join(root, "app.js"), "utf8");
const actions = fs.readFileSync(path.join(root, "battle-actions.js"), "utf8");
const execution = fs.readFileSync(path.join(root, "browser-execution.js"), "utf8");
const engine = fs.readFileSync(path.join(root, "browser-engine.js"), "utf8");
const formation = fs.readFileSync(path.join(root, "browser-formation.js"), "utf8");
const lab = fs.readFileSync(path.join(root, "battle-lab.js"), "utf8");
const dice = fs.readFileSync(path.join(root, "browser-dice.js"), "utf8");
const turbo = fs.readFileSync(path.join(root, "browser-turbo.js"), "utf8");
const css = fs.readFileSync(path.join(root, "battlefield.css"), "utf8");

assert.match(view, /MAX_SLOTS = 6/); assert.match(app, /MAX_SLOTS = 6/);
assert.match(view, /card-concentration/); assert.match(replay, /CONCENTRATING/);
assert.match(view, /IRON_PIT_COMBATANT_ART/);
assert.match(app, /Iron Pit ready\. Choose cards or load the sample matchup\./);
assert.match(app, /IRON_PIT_EXECUTION/); assert.match(app, /IRON_PIT_BATTLE_ACTIONS/);
assert.match(actions, /startLive/); assert.match(actions, /nextEvent/); assert.match(actions, /watchRest/); assert.match(actions, /replayTurbo/);
assert.match(execution, /function createSession/); assert.match(execution, /function resolveLive/); assert.match(execution, /function resolveReplay/); assert.match(execution, /async function runTurbo/);
assert.doesNotMatch(app, /runEncounter|runSeeded|runBatch|IRON_PIT_DICE\s*=/);
assert.doesNotMatch(lab, /createSeededDice|seedNumber/);
assert.match(lab, /function diagnosticId/);
assert.match(dice, /crypto\.getRandomValues/); assert.match(dice, /function clearHistory/); assert.match(dice, /function getHistory/);
assert.match(turbo, /function runSeeded/); assert.match(turbo, /async function runBatch/); assert.match(turbo, /finally \{ window\.IRON_PIT_DICE = prior; \}/);
assert.match(replay, /bindBattle/); assert.match(replay, /eventStep/); assert.match(replay, /syncFinal/);
assert.match(engine, /1-6 cards per side/); assert.match(engine, /IRON_PIT_BROWSER_FORMATION/);
assert.match(engine, /map_definition/); assert.match(engine, /IRON_PIT_BROWSER_ARENA_MAP/);
assert.match(formation, /HERO_FRONT = 5/); assert.match(formation, /MONSTER_FRONT = 10/);
assert.match(replay, /initiative-badge/); assert.match(replay, /critical-screen/); assert.match(replay, /fumble-blackout/);
assert.match(css, /\.battle-card\.turn-active/); assert.match(css, /card-turn-shake/); assert.match(css, /\.battle-card\.battle-dead/);
assert.ok(html.indexOf("browser-tactical-mind.js") < html.indexOf("browser-grapple.js"));
assert.ok(html.indexOf("browser-offense-value.js") < html.indexOf("browser-spell-offense.js"));
assert.ok(html.indexOf("browser-spell-offense.js") < html.indexOf("browser-turn.js"));
assert.ok(html.indexOf("browser-action-surge.js") < html.indexOf("browser-turn.js"));
assert.ok(html.indexOf("browser-formation.js") < html.indexOf("browser-arena-map.js"));
assert.ok(html.indexOf("browser-arena-map.js") < html.indexOf("browser-grid-geometry.js"));
assert.ok(html.indexOf("browser-grid-geometry.js") < html.indexOf("browser-grid-movement.js"));
assert.ok(html.indexOf("browser-grid-movement.js") < html.indexOf("browser-grid-placement.js"));
assert.ok(html.indexOf("browser-grid-placement.js") < html.indexOf("browser-engine.js"));
assert.ok(html.indexOf("figure-portraits.js") < html.indexOf("combatant-art.js"));
assert.ok(html.indexOf("combatant-art.js") < html.indexOf("battlefield-view.js"));
assert.ok(html.indexOf("battlefield-picker.js") < html.indexOf("app.js"));
assert.ok(html.indexOf("battlefield-view.js") < html.indexOf("app.js"));
assert.ok(html.indexOf("battlefield-replay.js") < html.indexOf("browser-execution.js"));
assert.ok(html.indexOf("browser-turbo.js") < html.indexOf("browser-execution.js"));
assert.ok(html.indexOf("turbo-view.js") < html.indexOf("browser-execution.js"));
assert.ok(html.indexOf("browser-execution.js") < html.indexOf("battle-actions.js"));
assert.ok(html.indexOf("battle-actions.js") < html.indexOf("app.js"));

console.log("production-path battlefield + universal execution wiring regression passed");
