"use strict";
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

try {
  const F = window.IRON_PIT_BROWSER_MULTIATTACK.attackSlotFeature;
  const action = {id: "attack", name: "Attack", isAttackAction: true};
  const variant = {id: "attack"};
  assert.equal(F(action, variant, 1), "attack");
  assert.equal(F(action, variant, 2), "extra-attack");
  assert.equal(F(action, variant, 3), "extra-attack");

  const monsterMulti = {id: "any-name", name: "Printed Multiattack",
    isAttackAction: false};
  assert.equal(F(monsterMulti, {id: "source-printed-sequence"}, 2),
    "source-printed-sequence");
  assert.throws(() => F(action, variant, 0), /slot index/);
  console.log("Universal Attack Action additional-slot attribution passed.");
} catch (error) {
  console.error("Universal Attack Action label regression failed.", error);
  throw error;
}
