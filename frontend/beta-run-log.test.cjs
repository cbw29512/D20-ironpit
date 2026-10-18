"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

function node() {
  return {
    children: [], open: false, textContent: "", listeners: {},
    get childElementCount() { return this.children.length; },
    append(...items) { this.children.push(...items); },
    replaceChildren(...items) { this.children = items; },
    addEventListener(name, callback) { (this.listeners[name] ||= []).push(callback); },
  };
}
const elements = new Map();
const get = (id) => {
  if (!elements.has(id)) elements.set(id, node());
  return elements.get(id);
};
const context = {
  window: { IRON_PIT_BATTLEFIELD_VIEW: { eventRow: (event) => ({ event }) } },
  document: { getElementById: get, createElement: node },
  console, JSON,
};
vm.runInNewContext(fs.readFileSync(path.join(__dirname, "beta-run-log.js"), "utf8"), context);
const log = context.window.IRON_PIT_BETA_LOG;
const selection = { ruleset: "2014", hero_ids: ["fighter"], monster_ids: ["goblin"] };
const battle = { rounds: 2, outcome: "heroes_win", events: [
  { round_number: 1, description: "Attack" },
  { round_number: 2, description: "Victory" },
] };
try {
  log.begin(selection, 1701);
  log.step(battle.events[0]);
  log.record(battle, selection, 1701, "Playback renderer crashed");
  assert.equal(log.entries().length, 1, "One attempt must produce one entry");
  assert.equal(log.entries()[0].outcome, "ERROR");
  assert.equal(log.entries()[0].failure, "Playback renderer crashed");
  assert.equal(log.entries()[0].events.length, 2, "Retain all resolved events, not just played events");
  log.begin(selection, 1702);
  log.finish(battle);
  assert.equal(log.entries().length, 2, "Next fight can proceed after failure");
  assert.equal(log.entries()[1].outcome, "heroes_win");
  console.log("Beta failure lifecycle test passed.");
} catch (error) {
  console.error("Beta failure lifecycle test failed", error);
  process.exitCode = 1;
}
