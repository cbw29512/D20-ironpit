"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

load("browser-defensive-modifier-rules.js");
load("browser-targeting-wards.js");

let nextSave = false;
window.IRON_PIT_BROWSER_SAVES = {
  resolveSavingThrow: (_state, ability, dc) => ({
    roll: { notation: "1d20", rolls: [nextSave ? 20 : 1], modifier: 0, total: nextSave ? 20 : 1 },
    succeeded: nextSave,
    ability,
    dc,
  }),
};

const ward = {
  id: "druid14:natures-sanctuary:passive:0",
  source_id: "druid14",
  source_effect_id: "natures-sanctuary",
  source_name: "Nature's Sanctuary",
  kind: "targeting-save-gate",
  source_creature_types: ["beast", "plant"],
  save_ability: "wisdom",
  save_dc: 18,
  ends_on_owner_attack: false,
  success_immunity_hours: 24,
};

const target = {
  combatant_id: "druid14",
  state: { template: { name: "Thalen Greenbough" }, active_modifiers: [ward] },
};
const attacker = (type) => ({
  combatant_id: `attacker-${type}`,
  state: {
    template: { name: `Test ${type}`, creature_type: type },
    active_modifiers: [],
    targeting_gate_immunity_keys: [],
  },
});

const beast = attacker("beast");
const plant = attacker("plant");
const humanoid = attacker("humanoid");

nextSave = false;
const failed = window.IRON_PIT_BROWSER_TARGETING_WARDS.check(beast, target);
assert.ok(failed);
assert.equal(failed.succeeded, false);
assert.equal(failed.gate.source_effect_id, "natures-sanctuary");

assert.ok(window.IRON_PIT_BROWSER_TARGETING_WARDS.check(plant, target));
assert.equal(window.IRON_PIT_BROWSER_TARGETING_WARDS.check(humanoid, target), null);

nextSave = true;
const succeeded = window.IRON_PIT_BROWSER_TARGETING_WARDS.check(beast, target);
assert.ok(succeeded);
assert.equal(succeeded.succeeded, true);
assert.deepEqual(beast.state.targeting_gate_immunity_keys, [
  "druid14:druid14:natures-sanctuary:passive:0",
]);

nextSave = false;
assert.equal(window.IRON_PIT_BROWSER_TARGETING_WARDS.check(beast, target), null);

console.log("Browser typed targeting gate and success-immunity regressions passed.");
