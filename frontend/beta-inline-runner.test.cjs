"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const elements = new Map();
function element(id) {
  if (!elements.has(id)) elements.set(id, {
    id, value: "", textContent: "", disabled: false, max: 0,
    listeners: {}, addEventListener(type, callback) { this.listeners[type] = callback; },
  });
  return elements.get(id);
}
global.document = { getElementById: element };
element("beta-run-edition").value = "2014";
element("beta-suite").value = "roster";
element("beta-repeats").value = "1";
window.IRON_PIT_BROWSER_CATALOG = { buildCatalog: async () => ({
  heroes: [{ coverage_status: "raw_ready", runnable_template_id: "hero-template" }],
  monsters: [{ coverage_status: "raw_ready", runnable_template_id: "monster-template" }],
}) };
window.IRON_PIT_COMBAT_PRESETS = { recipes: [], resolve: () => ({ heroes: [], monsters: [] }) };
window.IRON_PIT_COMBAT_PRESET_RECIPES = { recipes: [] };
const battle = { events: [{ event_type: "damage", round_number: 1, description: "test event" }],
  outcome: "heroes_win", rounds: 1 };
window.IRON_PIT_BROWSER_TURBO = { runSeeded: () => ({ battle }) };
window.IRON_PIT_BETA_BRIDGE = { ready: () => true, showFight: async () => { throw Error("spectator render failed"); } };
const recorded = [];
window.IRON_PIT_BETA_LOG = { record: (...args) => recorded.push(args) };
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "beta-inline-runner.js"), "utf8"),
  { filename: "beta-inline-runner.js" });

(async () => {
  await element("beta-run-all").listeners.click();
  assert.equal(recorded.length, 1);
  assert.equal(recorded[0][0], battle, "failed fight must retain its actual battle object");
  assert.deepEqual(recorded[0][0].events, battle.events, "failure report must retain full event log");
  assert.equal(recorded[0][3], "spectator render failed");
  console.log("Beta inline runner preserves battle events on playback failure.");
})().catch((error) => { console.error(error); process.exitCode = 1; });
