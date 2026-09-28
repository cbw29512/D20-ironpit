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

load("browser-state.js");
load("browser-miss-to-hit-override.js");

const template = {
  name: "Peerless Aim Test",
  max_hp: 100,
  speed_ft: 30,
  resources: { "boon-combat-prowess": 1 },
  start_turn_resource_refill_ids: ["boon-combat-prowess"],
  miss_to_hit_override_resource_id: "boon-combat-prowess",
  miss_to_hit_override_source_name: "Boon of Combat Prowess",
  traits: [],
};
const state = window.IRON_PIT_BROWSER_STATE.buildState(template);

const first = window.IRON_PIT_BROWSER_MISS_TO_HIT_OVERRIDE.apply(state, false);
assert.equal(first.hit, true);
assert.equal(first.sourceName, "Boon of Combat Prowess");
assert.equal(state.resources["boon-combat-prowess"], 0);

const second = window.IRON_PIT_BROWSER_MISS_TO_HIT_OVERRIDE.apply(state, false);
assert.equal(second.hit, false);

window.IRON_PIT_BROWSER_STATE.refreshStartOfTurn(state);
assert.equal(state.resources["boon-combat-prowess"], 1);

const third = window.IRON_PIT_BROWSER_MISS_TO_HIT_OVERRIDE.apply(state, false);
assert.equal(third.hit, true);
assert.equal(state.resources["boon-combat-prowess"], 0);

console.log("Browser turn-start resource refill reuses miss-to-hit override correctly.");
