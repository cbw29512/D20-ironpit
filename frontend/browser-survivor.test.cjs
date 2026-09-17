"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
window.IRON_PIT_BROWSER_GRAPPLE = { speedIsZero: () => false };
window.IRON_PIT_BROWSER_MODIFIERS = { effectiveSpeed: (state) => state.template.speed_ft };
window.IRON_PIT_BROWSER_CONDITION_RULES = { incapacitated: (state) => state.is_unconscious };
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-state.js"), "utf8"), { filename: "browser-state.js" });

const S = window.IRON_PIT_BROWSER_STATE;
const template = (amount = 9) => ({
  name: "Champion", kind: "character", max_hp: 100, speed_ft: 30,
  survivor_heal_amount: amount, resources: {}, traits: [], size: "medium",
});

{
  const state = S.buildState(template());
  state.current_hp = 50;
  S.beginTurn(state);
  assert.equal(state.current_hp, 59, "Survivor heals at exactly half HP");
}
{
  const state = S.buildState(template());
  state.current_hp = 51;
  S.beginTurn(state);
  assert.equal(state.current_hp, 51, "Survivor does not heal above half HP");
}
{
  const state = S.buildState(template());
  state.current_hp = 0;
  S.beginTurn(state);
  assert.equal(state.current_hp, 0, "Survivor does not heal a 0-HP creature");
}
{
  const state = S.buildState(template(10));
  state.max_hp_bonus = 20;
  state.current_hp = 60;
  S.beginTurn(state);
  assert.equal(state.current_hp, 70, "Survivor uses effective maximum HP for its half-HP threshold");
}

console.log("Browser Survivor start-turn healing matches compiled RAW thresholds.");
