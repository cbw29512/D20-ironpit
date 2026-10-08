const assert = require("assert");
const fs = require("fs");
const vm = require("vm");
global.window = global;
function load(file) {
  vm.runInThisContext(fs.readFileSync(__dirname + "/" + file, "utf8"), { filename: file });
}

window.IRON_PIT_DICE = { values: [6], roll() { return this.values.shift(); } };
window.IRON_PIT_BROWSER_STATE = { effectiveMaxHp: (state) => state.template.max_hp };
window.IRON_PIT_BROWSER_ABILITY_HOOKS = null;
load("browser-turn-start-effects.js");

const rule = {
  sourceId: "test-threshold-state",
  sourceName: "Threshold State",
  effectId: "test-threshold-state-active",
  maxCurrentHp: 40,
  dieSize: 6,
  minimumRoll: 6,
  endsOnFullHp: true,
};
const member = {
  combatant_id: "construct",
  state: {
    template: { name: "Test Construct", max_hp: 100, turn_start_persistent_effects: [rule] },
    current_hp: 40,
    active_effect_ids: [],
  },
};

let result = window.IRON_PIT_BROWSER_TURN_START_EFFECTS.resolveStartOfTurn(1, 1, member);
assert.equal(result.events.length, 1);
assert.equal(result.events[0].feature_roll.total, 6);
assert.deepEqual(member.state.active_effect_ids, ["test-threshold-state-active"]);

window.IRON_PIT_DICE.values = [1];
result = window.IRON_PIT_BROWSER_TURN_START_EFFECTS.resolveStartOfTurn(2, 2, member);
assert.equal(result.events.length, 0);

member.state.current_hp = 100;
assert.deepEqual(
  window.IRON_PIT_BROWSER_TURN_START_EFFECTS.syncAfterHpChange(member.state),
  ["test-threshold-state-active"],
);
assert.deepEqual(member.state.active_effect_ids, []);

console.log("Browser turn-start persistent effect parity passed.");
