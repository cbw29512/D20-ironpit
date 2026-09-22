"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-miss-to-hit.js"), "utf8"),
  { filename: "browser-miss-to-hit.js" },
);

const M = window.IRON_PIT_BROWSER_MISS_TO_HIT;
const state = (enabled = true) => ({
  template: { miss_to_hit_once_per_turn: enabled },
  feature_last_turn_keys: {},
});

assert.deepEqual(M.resolve(state(false), false, "1:a"), { hit: false, used: false });
assert.deepEqual(M.resolve(state(true), true, "1:a"), { hit: true, used: false });

const rogue = state(true);
assert.deepEqual(M.resolve(rogue, false, "1:a"), { hit: true, used: true });
assert.deepEqual(M.resolve(rogue, false, "1:a"), { hit: false, used: false });
assert.deepEqual(M.resolve(rogue, false, "2:a"), { hit: true, used: true });

const noTurn = state(true);
assert.deepEqual(M.resolve(noTurn, false, null), { hit: false, used: false });
assert.deepEqual(noTurn.feature_last_turn_keys, {});

for (const htmlName of ["index.html", path.join("..", "index.html")]) {
  const html = fs.readFileSync(path.join(__dirname, htmlName), "utf8");
  assert.match(html, /browser-miss-to-hit\.js/);
  assert.ok(
    html.indexOf("browser-miss-to-hit.js") < html.indexOf("browser-attack.js"),
    "miss-to-hit primitive must load before browser attack resolution",
  );
}

console.log("Browser generic once-per-turn miss-to-hit regressions passed.");
