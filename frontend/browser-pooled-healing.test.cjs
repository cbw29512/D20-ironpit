"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(`frontend/${name}`, "utf8"),
  { filename: name },
);

window.IRON_PIT_BROWSER_STATE = {
  effectiveMaxHp: (state) => state.template.max_hp + (state.max_hp_bonus || 0),
};
window.IRON_PIT_BROWSER_HEALING = {
  restore: (state, amount) => {
    if (amount <= 0 || state.is_dead) return 0;
    const before = state.current_hp;
    state.current_hp = Math.min(
      window.IRON_PIT_BROWSER_STATE.effectiveMaxHp(state),
      before + amount,
    );
    const healed = state.current_hp - before;
    if (healed > 0) {
      state.is_alive = true;
      state.is_unconscious = false;
      state.is_stable = false;
      state.death_save_successes = 0;
      state.death_save_failures = 0;
    }
    return healed;
  },
};

load("browser-pooled-healing.js");
const P = window.IRON_PIT_BROWSER_POOLED_HEALING;

function member(id, hp, maxHp = 10, maxHpBonus = 0) {
  return {
    combatant_id: id,
    state: {
      template: { name: id, max_hp: maxHp },
      max_hp_bonus: maxHpBonus,
      current_hp: hp,
      is_alive: true,
      is_dead: false,
      is_unconscious: hp === 0,
      is_stable: false,
      death_save_successes: 0,
      death_save_failures: 0,
    },
  };
}

const first = member("first", 0, 10);
const second = member("second", 1, 10);
assert.equal(P.capacity(first, 1, 2), 5);
assert.equal(P.capacity(second, 1, 2), 4);

const result = P.resolve([first, second], 7, 1, 2);
assert.deepEqual(result.allocations.map((item) => [item.targetId, item.healed]), [
  ["first", 5],
  ["second", 2],
]);
assert.equal(result.remaining, 0);
assert.equal(first.state.current_hp, 5);
assert.equal(second.state.current_hp, 3);
assert.equal(first.state.is_unconscious, false);

const boosted = member("boosted", 5, 10, 6);
assert.equal(P.capacity(boosted, 1, 2), 3, "cap uses effective maximum HP");

assert.throws(() => P.capacity(first, 2, 1), /positive fraction/);
assert.throws(() => P.resolve([], 5, 1, 2), /at least one target/);

console.log("Universal browser pooled-healing regressions passed.");
