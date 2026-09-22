const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = {};
global.console = console;
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-miss-to-hit.js"), "utf8"));

const M = window.IRON_PIT_BROWSER_MISS_TO_HIT;
const state = (enabled = true) => ({
  template: { miss_to_hit_once_per_turn: enabled },
  feature_last_turn_keys: {},
});

assert.deepEqual(M.resolve(state(false), false, "1:a"), { hit: false, used: false });
assert.deepEqual(M.resolve(state(true), true, "1:a"), { hit: true, used: false });

const fighter = state(true);
assert.deepEqual(M.resolve(fighter, false, "1:a"), { hit: true, used: true });
assert.deepEqual(M.resolve(fighter, false, "1:a"), { hit: false, used: false });
assert.deepEqual(M.resolve(fighter, false, "2:a"), { hit: true, used: true });

const noTurn = state(true);
assert.deepEqual(M.resolve(noTurn, false, null), { hit: false, used: false });
assert.deepEqual(noTurn.feature_last_turn_keys, {});

console.log("browser miss-to-hit tests passed");
