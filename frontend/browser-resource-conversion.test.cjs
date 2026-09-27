const assert = require("assert");
const fs = require("fs");
const vm = require("vm");

global.window = {};
vm.runInThisContext(fs.readFileSync("frontend/browser-action-economy.js", "utf8"));
vm.runInThisContext(fs.readFileSync("frontend/browser-resources.js", "utf8"));
vm.runInThisContext(fs.readFileSync("frontend/browser-ability-hooks.js", "utf8"));
vm.runInThisContext(fs.readFileSync("frontend/browser-resource-conversion.js", "utf8"));

const C = window.IRON_PIT_BROWSER_RESOURCE_CONVERSION;
const action = {
  id: "create-spell-slot-1",
  name: "Font of Magic: Create 1st-Level Spell Slot",
  actionCost: "bonus_action",
  sourceResourceId: "sorcery-points",
  sourceCost: 2,
  targetResourceId: "spell-slot-1",
  targetGain: 1,
  targetAllowsOverflow: true,
  automation: "when-all-spell-slots-empty",
  priority: 10,
};
function member() {
  return {
    combatant_id: "nyra",
    state: {
      template: {
        name: "Nyra",
        ruleset: "2014",
        resources: { "spell-slot-1": 3, "sorcery-points": 2 },
        resource_conversion_actions: [action],
        unlimited_resources: [],
      },
      resources: { "spell-slot-1": 0, "sorcery-points": 2 },
      action_available: true,
      bonus_action_available: true,
      reaction_available: true,
      is_dead: false,
      is_unconscious: false,
      turn_terminated: false,
    },
  };
}

const nyra = member();
assert.equal(C.allSpellSlotsEmpty(nyra.state), true);
assert.equal(C.automaticAction(nyra.state).id, "create-spell-slot-1");
const event = C.resolve(1, 1, nyra, action);
assert.equal(nyra.state.resources["sorcery-points"], 0);
assert.equal(nyra.state.resources["spell-slot-1"], 1);
assert.equal(nyra.state.bonus_action_available, false);
assert.equal(event.feature_id, "create-spell-slot-1");

const overflow = member();
overflow.state.resources["spell-slot-1"] = 3;
assert.equal(C.resolve(1, 1, overflow, action).feature_id, "create-spell-slot-1");
assert.equal(overflow.state.resources["spell-slot-1"], 4);

const empty = member();
empty.state.resources["sorcery-points"] = 0;
assert.equal(C.available(empty.state, action), false);

console.log("Browser resource conversion regressions passed.");
