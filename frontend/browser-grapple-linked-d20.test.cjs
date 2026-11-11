"use strict";
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

try {
  const G = window.IRON_PIT_BROWSER_GRAPPLE;
  const State = window.IRON_PIT_BROWSER_STATE;
  const checks = window.IRON_PIT_BROWSER_ABILITY_CHECKS;
  const saves = window.IRON_PIT_BROWSER_SAVING_THROWS;
  const card = structuredClone(window.IRON_PIT_BROWSER_MONSTERS_2014["2014-giant-crab"]);
  assert.ok(card);
  const state = State.buildState(card);
  assert.equal(G.checkSaveDisadvantage(state, "strength"), 0);
  G.apply(state, "synthetic-holder", 15, 50, true, false, null, {
    checkSaveDisadvantageAbilities: ["strength"],
  });
  assert.equal(G.checkSaveDisadvantage(state, "strength"), 1);
  assert.equal(G.checkSaveDisadvantage(state, "dexterity"), 0);
  assert.equal(checks.mode(state, 0, 0, { ability: "strength" }), "disadvantage");
  assert.equal(saves.saveMode(state, "strength"), "disadvantage");
  assert.equal(saves.saveMode(state, "constitution"), "normal");
  G.release(state, "synthetic-holder");
  assert.equal(G.checkSaveDisadvantage(state, "strength"), 0);
  assert.equal(checks.mode(state, 0, 0, { ability: "strength" }), "normal");
  assert.equal(saves.saveMode(state, "strength"), "normal");
  console.log("Universal source-owned Grapple check/save penalty browser parity passed");
} catch (error) {
  console.error("Grapple-linked d20 browser regression failed", error);
  throw error;
}
