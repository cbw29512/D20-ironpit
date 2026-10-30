const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

global.window = {};
function load(name) {
  try {
    return vm.runInThisContext(
      fs.readFileSync(path.join(__dirname, name), "utf8"),
      { filename: name },
    );
  } catch (error) {
    console.error("Failed to load browser damage source test dependency.", { name, error });
    throw error;
  }
}

window.IRON_PIT_BROWSER_STATE = {
  effectiveMaxHp: (state) => state.template.max_hp,
};
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };

load("browser-turn-damage-source.js");
load("browser-zero-hp.js");

const state = {
  template: {
    name: "Target",
    kind: "monster",
    max_hp: 100,
    traits: [],
    combat_traits: [],
    damage_taken_timed_effects: [],
  },
  current_hp: 100,
  temporary_hp: 0,
  is_alive: true,
  is_dead: false,
  is_unconscious: false,
  is_stable: false,
  active_effect_ids: [],
  timed_effects: [],
  damage_taken_this_turn_by_type: {},
  damage_taken_this_turn_by_source: {},
  damage_types_taken_since_regen: [],
  damage_share_source_id: null,
  concentration: null,
};

window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(
  state, 7, false, [], [], null, [], "attacker-a",
);
window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(
  state, 5, false, [], [], null, [], "attacker-a",
);
window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(
  state, 3, false, [], [], null, [], "attacker-b",
);
window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(
  state, 2, false, [], [], null, [],
);

assert.deepEqual(state.damage_taken_this_turn_by_source, {
  "attacker-a": 12,
  "attacker-b": 3,
});

window.IRON_PIT_BROWSER_TURN_DAMAGE_SOURCE.clear(state);
assert.deepEqual(state.damage_taken_this_turn_by_source, {});

console.log("browser damage source ledger ok");
