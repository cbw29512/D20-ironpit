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

window.IRON_PIT_BROWSER_TIMED = {
  resolveMovementCounters: () => [],
  suppressesAction: () => false,
  suppressesBonusAction: () => false,
  suppressesMovement: () => false,
  suppressesReactions: () => false,
};
window.IRON_PIT_BROWSER_MODIFIERS = { effectiveSpeed: (state) => state.template.speed_ft || 30 };
window.IRON_PIT_BROWSER_CONDITION_RULES = { incapacitated: () => false };

load("browser-state.js");
load("browser-miss-to-hit-override.js");

const template = {
  name: "Karnok Stoneward",
  speed_ft: 30,
  max_hp: 213,
  resources: { "boon-combat-prowess": 1 },
  miss_to_hit_override_resource_id: "boon-combat-prowess",
  miss_to_hit_override_source_name: "Boon of Combat Prowess",
  turn_start_resource_refill_ids: ["boon-combat-prowess"],
};
const state = window.IRON_PIT_BROWSER_STATE.buildState(template);
const override = window.IRON_PIT_BROWSER_MISS_TO_HIT_OVERRIDE;

const first = override.apply(state, false);
assert.deepEqual(first, {
  hit: true,
  featureId: "boon-combat-prowess",
  sourceName: "Boon of Combat Prowess",
});
assert.equal(state.resources["boon-combat-prowess"], 0);

const second = override.apply(state, false);
assert.deepEqual(second, { hit: false, featureId: null, sourceName: null });

window.IRON_PIT_BROWSER_STATE.beginTurn(state);
assert.equal(state.resources["boon-combat-prowess"], 1);

const nextTurn = override.apply(state, false);
assert.equal(nextTurn.hit, true);
assert.equal(nextTurn.sourceName, "Boon of Combat Prowess");

console.log("Browser Fighter 19 Combat Prowess turn-reset parity passed.");
