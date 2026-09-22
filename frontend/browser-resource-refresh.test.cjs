const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

load("browser-resource-refresh.js");
load("browser-state.js");
load("browser-miss-to-hit-override.js");

const template = {
  name: "Universal refresh fixture",
  max_hp: 10,
  speed_ft: 30,
  resources: { "boon-combat-prowess": 1 },
  start_of_turn_resource_refresh_ids: ["boon-combat-prowess"],
  miss_to_hit_override_resource_id: "boon-combat-prowess",
  miss_to_hit_override_source_name: "Boon of Combat Prowess",
  traits: [],
};
const state = window.IRON_PIT_BROWSER_STATE.buildState(template);

let result = window.IRON_PIT_BROWSER_MISS_TO_HIT_OVERRIDE.apply(state, false);
assert.deepEqual(result, {
  hit: true,
  featureId: "boon-combat-prowess",
  sourceName: "Boon of Combat Prowess",
});
assert.equal(state.resources["boon-combat-prowess"], 0);

result = window.IRON_PIT_BROWSER_MISS_TO_HIT_OVERRIDE.apply(state, false);
assert.equal(result.hit, false);

window.IRON_PIT_BROWSER_STATE.beginTurn(state);
assert.equal(state.resources["boon-combat-prowess"], 1);

result = window.IRON_PIT_BROWSER_MISS_TO_HIT_OVERRIDE.apply(state, false);
assert.equal(result.hit, true);
assert.equal(state.resources["boon-combat-prowess"], 0);

console.log("Browser start-of-turn resource refresh regressions passed.");
