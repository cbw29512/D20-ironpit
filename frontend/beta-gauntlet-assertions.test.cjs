"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const test = require("node:test");
function api() {
  const context = { window: {} };
  const source = fs.readFileSync(path.join(__dirname, "beta-gauntlet-assertions.js"), "utf8");
  vm.runInNewContext(source, context, { filename: "beta-gauntlet-assertions.js" });
  return context.window.IRON_PIT_BETA_GAUNTLET_ASSERTIONS;
}
test("gauntlet records combat families with reproducible context", () => {
  const a = api();
  const observed = a.inspect({ events: [
    { event_type: "attack", round_number: 1, hit: true, critical: true, feature_id: "slash",
      applied_condition_ids: ["prone"], damage_components: [{ damage_type: "slashing", total: 10 }] },
    { event_type: "healing", round_number: 2, resource_remaining: 1 },
    { event_type: "victory", round_number: 2 },
  ] });
  assert.equal(observed.families.includes("critical hits"), true);
  assert.equal(observed.families.includes("healing"), true);
  assert.equal(observed.families.includes("prone"), true);
  assert.equal(observed.families.includes("death and victory"), true);
  const coverage = a.aggregate([{ name: "test", edition: "2014", seed: 21, result: "PASS", observed }]);
  assert.equal(coverage["critical hits"].fights, 1);
  assert.equal(coverage["critical hits"].sample.seed, 21);
  assert.equal(coverage["ranged attacks"].fights, 0);
});
test("malformed or nonterminal fights fail rather than inflate coverage", () => {
  const a = api();
  assert.throws(() => a.inspect({ events: [{ round_number: -1, event_type: "healing" }] }), /Malformed/);
  assert.throws(() => a.inspect({ events: [{ round_number: 1, event_type: "healing" }] }), /terminal/);
  assert.equal(a.aggregate([{ result: "FAIL", observed: { families: ["healing"] } }]).healing.fights, 0);
});
