"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-recharge.js"), "utf8"), { filename: "browser-recharge.js" });

const R = window.IRON_PIT_BROWSER_RECHARGE;
const member = (uses = 0) => ({
  combatant_id: "recharge-monster",
  state: {
    resources: { breath: uses },
    template: { name: "Recharge Monster", recharge_rules: [{ resourceId: "breath", minimumRoll: 5, dieSize: 6 }] },
  },
});
const dice = (values) => ({ roll: (sides) => { assert.equal(sides, 6); if (!values.length) throw new Error("Unexpected roll"); return values.shift(); } });

{
  const actor = member(1); window.IRON_PIT_DICE = dice([]);
  const result = R.resolveStartOfTurn(10, 2, actor);
  assert.equal(result.events.length, 0, "Available Recharge resources never roll");
  assert.equal(result.sequence, 10); assert.equal(actor.state.resources.breath, 1);
}
{
  const actor = member(0); window.IRON_PIT_DICE = dice([4]);
  const result = R.resolveStartOfTurn(20, 3, actor);
  assert.equal(result.events.length, 1); assert.equal(result.events[0].recharge_succeeded, false);
  assert.equal(result.events[0].resource_remaining, 0); assert.equal(actor.state.resources.breath, 0);
  assert.equal(result.sequence, 21);
}
{
  const actor = member(0); window.IRON_PIT_DICE = dice([5]);
  const result = R.resolveStartOfTurn(30, 4, actor);
  assert.equal(result.events[0].recharge_succeeded, true); assert.equal(actor.state.resources.breath, 1);
  assert.equal(result.events[0].recharge_roll.total, 5);
}
{
  const actor = member(0); actor.state.template.recharge_rules[0].minimumRoll = 6; window.IRON_PIT_DICE = dice([5]);
  assert.equal(R.resolveStartOfTurn(40, 5, actor).events[0].recharge_succeeded, false);
}
{
  const actor = member(0); actor.state.template.recharge_rules[0].resourceId = "missing"; window.IRON_PIT_DICE = dice([]);
  assert.throws(() => R.resolveStartOfTurn(50, 6, actor), /missing resource/);
}

console.log("Browser Recharge lifecycle regression passed.");