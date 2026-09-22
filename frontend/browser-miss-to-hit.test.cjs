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

load("browser-miss-to-hit.js");
const missToHit = window.IRON_PIT_BROWSER_MISS_TO_HIT;

function state(enabled = true) {
  return {
    template: { miss_to_hit_once_per_turn: enabled },
    feature_last_turn_keys: {},
  };
}

{
  const actor = state(false);
  assert.deepEqual(
    missToHit.resolve(actor, false, "round-1:hero"),
    { hit: false, used: false },
    "disabled content must preserve a miss",
  );
}

{
  const actor = state(true);
  assert.deepEqual(
    missToHit.resolve(actor, true, "round-1:hero"),
    { hit: true, used: false },
    "an existing hit must not consume the feature",
  );
  assert.deepEqual(actor.feature_last_turn_keys, {});
}

{
  const actor = state(true);
  const first = missToHit.resolve(actor, false, "round-1:hero");
  const second = missToHit.resolve(actor, false, "round-1:hero");
  const nextTurn = missToHit.resolve(actor, false, "round-2:hero");

  assert.deepEqual(first, { hit: true, used: true }, "first miss converts to a hit");
  assert.deepEqual(second, { hit: false, used: false }, "same-turn second miss stays a miss");
  assert.deepEqual(nextTurn, { hit: true, used: true }, "a new turn re-enables the conversion");
}

{
  const actor = state(true);
  assert.deepEqual(
    missToHit.resolve(actor, false, null),
    { hit: false, used: false },
    "missing turn identity must fail closed",
  );
  assert.deepEqual(actor.feature_last_turn_keys, {});
}

{
  const actor = { template: { miss_to_hit_once_per_turn: true } };
  assert.deepEqual(
    missToHit.resolve(actor, false, "round-1:hero"),
    { hit: true, used: true },
    "runtime initializes shared once-per-turn state when absent",
  );
  assert.equal(
    actor.feature_last_turn_keys[missToHit.FEATURE_ID],
    "round-1:hero",
  );
}

console.log("browser miss-to-hit primitive tests passed");
