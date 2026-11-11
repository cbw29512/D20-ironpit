"use strict";
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

try {
  const control = window.IRON_PIT_BROWSER_BODY_CONTROL;
  const State = window.IRON_PIT_BROWSER_STATE;
  const card = structuredClone(window.IRON_PIT_BROWSER_MONSTERS_2014["2014-giant-crab"]);
  assert.ok(card);
  const owner = State.buildState(card);
  const host = State.buildState(card);
  assert.equal(owner.controlled_by, null);
  assert.deepEqual(host.controlling_target_ids, []);
  const options = {
    sourceActionId: "generic-control", sourceName: "Printed Body Control",
    roundNumber: 2, failedSave: true,
  };
  assert.equal(control.begin("owner", owner, "host", host, {...options, failedSave: false}), false);
  assert.equal(control.begin("owner", owner, "host", host, options), true);
  assert.equal(host.controlled_by.source_id, "owner");
  assert.equal(host.controlled_by.host_id, "host");
  assert.equal(host.controlled_by.started_round, 2);
  assert.deepEqual(owner.controlling_target_ids, ["host"]);
  assert.equal(control.begin("owner", owner, "other", State.buildState(card), options), false);
  assert.equal(control.end("wrong", owner, "host", host), false);
  assert.equal(control.end("owner", owner, "host", host), true);
  assert.equal(host.controlled_by, null);
  assert.deepEqual(owner.controlling_target_ids, []);
  assert.equal(control.begin("same", owner, "same", host, options), false);
  console.log("Universal body-control state/ownership browser parity passed.");
} catch (error) {
  console.error("Universal body-control link browser regression failed", error);
  throw error;
}
