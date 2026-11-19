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
// Terminal effects can kill while positive HP remains (e.g., Pit Petrified).
source.state.current_hp = 9;
assert.equal(window.IRON_PIT_BROWSER_DEATH_TRIGGER_SAVE.resolve(
  source, target, { save: { name: "Terminal Death" } }, save,
), "Terminal Death");
assert.equal(calls.length, 3);
// A living source cannot fire the trigger even if HP is zero.
source.state.is_dead = false;
assert.throws(() => window.IRON_PIT_BROWSER_DEATH_TRIGGER_SAVE.resolve(
  source, target, { save: { name: "Living Source" } }, save,
), /Death trigger source is not dead/);
assert.equal(calls.length, 3);
source.state.is_dead = true;
target.state.is_dead = true;
assert.equal(window.IRON_PIT_BROWSER_DEATH_TRIGGER_SAVE.resolve(
  source, target, { save: { name: "Pulse" } }, save,
), null);
assert.equal(calls.length, 3);
console.log("Browser death-trigger save delegation passed.");
