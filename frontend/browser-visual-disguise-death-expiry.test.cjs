"use strict";
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();
const S = window.IRON_PIT_BROWSER_STATE;
const Zero = window.IRON_PIT_BROWSER_ZERO_HP;
const Terminal = window.IRON_PIT_BROWSER_TERMINAL_EFFECTS;
const Exhaustion = window.IRON_PIT_BROWSER_EXHAUSTION;
const Pre = window.IRON_PIT_BROWSER_PRECOMBAT_BUFFS;
const original = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-commoner"];
assert.ok(original);
const card = {
  ...structuredClone(original),
  name: "Renamed magical disguise user",
  kind: "monster",
  visualDisguiseAction: {
    id: "visual-disguise", name: "Imaginary Veil", endsIfOwnerDead: true,
  },
};
const before = JSON.stringify(card);
const fresh = () => {
  const state = S.buildState(card);
  state.magical_visual_disguise_active = true;
  return state;
};
for (const pathway of ["damage-zero", "terminal", "exhaustion"]) {
  const state = fresh();
  if (pathway === "damage-zero") assert.equal(Zero.reduceToZero(state), "dead");
  else if (pathway === "terminal") assert.equal(Terminal.applyTerminalDeath(state), "dead");
  else assert.equal(Exhaustion.gain(state, 6), 6);
  assert.equal(state.is_dead, true);
  assert.equal(state.magical_visual_disguise_active, false, pathway);
  assert.equal(Pre.endIfOwnerDead(state), false, "Expiry is idempotent.");
}
{
  const state = fresh();
  state.is_unconscious = true;
  assert.equal(Pre.endIfOwnerDead(state), false, "Unconscious is not death.");
  assert.equal(state.magical_visual_disguise_active, true);
}
{
  const persistent = { ...card, kind: "character",
    visualDisguiseAction: { ...card.visualDisguiseAction, endsIfOwnerDead: false } };
  const state = S.buildState(persistent);
  state.magical_visual_disguise_active = true;
  Terminal.applyTerminalDeath(state);
  assert.equal(state.magical_visual_disguise_active, true,
    "Different source cards can declare a different death lifecycle.");
}
assert.equal(JSON.stringify(card), before, "Source card must remain immutable.");
console.log("Card-owned visual disguise expiration on ordinary/instant/exhaustion death passed.");
