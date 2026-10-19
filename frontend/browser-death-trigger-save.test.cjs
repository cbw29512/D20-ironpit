"use strict";
const assert = require("node:assert/strict");
global.window = globalThis;
require("./browser-death-trigger-save.js");

const source = { state: { is_dead: true, current_hp: 0 } };
const target = { state: { is_dead: false } };
const calls = [];
const save = (rule, options) => {
  calls.push({ rule, options });
  return rule.name;
};
for (const name of ["Synthetic Pulse", "Renamed Homebrew"]) {
  const result = window.IRON_PIT_BROWSER_DEATH_TRIGGER_SAVE.resolve(
    source, target, { save: { name } }, save,
  );
  assert.equal(result, name);
  assert.deepEqual(calls.at(-1).options, {
    spendAction: false, checkResource: false, spendResource: false,
  });
}
target.state.is_dead = true;
assert.equal(window.IRON_PIT_BROWSER_DEATH_TRIGGER_SAVE.resolve(
  source, target, { save: { name: "Pulse" } }, save,
), null);
assert.equal(calls.length, 2);
console.log("Browser death-trigger save delegation passed.");
