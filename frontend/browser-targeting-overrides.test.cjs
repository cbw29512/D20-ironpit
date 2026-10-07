const assert = require("assert");
const fs = require("fs");
const vm = require("vm");

global.window = global;
function load(file) {
  vm.runInThisContext(fs.readFileSync(__dirname + "/" + file, "utf8"), { filename: file });
}

window.IRON_PIT_DICE = {
  values: [6],
  roll() {
    if (!this.values.length) throw new Error("No fixed browser dice remain.");
    return this.values.shift();
  },
};
window.IRON_PIT_BROWSER_STATE = {
  effectiveMaxHp: (state) => state.template.max_hp,
};
window.IRON_PIT_BROWSER_HEALING_POLICY = { swarm: () => false };

load("browser-targeting-overrides.js");
load("browser-healing.js");

const rule = {
  sourceId: "test-turn-start-override",
  sourceName: "Test Override",
  maxCurrentHp: 40,
  dieSize: 6,
  minimumRoll: 6,
  endsOnFullHp: true,
};

function member(hp = 40) {
  return {
    combatant_id: "actor",
    state: {
      template: {
        name: "Test Override",
        max_hp: 100,
        turn_start_targeting_overrides: [rule],
      },
      current_hp: hp,
      is_alive: true,
      is_dead: false,
      is_unconscious: false,
      is_stable: false,
      death_save_successes: 0,
      death_save_failures: 0,
      active_targeting_override_ids: [],
    },
  };
}

const actor = member();
let result = window.IRON_PIT_BROWSER_TARGETING_OVERRIDES.resolveStartOfTurn(1, 1, actor);
assert.equal(result.events.length, 1);
assert.equal(result.events[0].feature_roll.total, 6);
assert.deepEqual(actor.state.active_targeting_override_ids, ["test-turn-start-override"]);

window.IRON_PIT_DICE.values = [1];
result = window.IRON_PIT_BROWSER_TARGETING_OVERRIDES.resolveStartOfTurn(2, 2, actor);
assert.equal(result.events.length, 0);
assert.deepEqual(actor.state.active_targeting_override_ids, ["test-turn-start-override"]);

const failed = member();
window.IRON_PIT_DICE.values = [5];
result = window.IRON_PIT_BROWSER_TARGETING_OVERRIDES.resolveStartOfTurn(3, 1, failed);
assert.equal(result.events[0].feature_roll.total, 5);
assert.deepEqual(failed.state.active_targeting_override_ids, []);

actor.state.current_hp = 99;
assert.equal(window.IRON_PIT_BROWSER_HEALING.restore(actor.state, 1), 1);
assert.equal(actor.state.current_hp, 100);
assert.deepEqual(actor.state.active_targeting_override_ids, []);

console.log("Browser targeting override activation lifecycle passed.");
