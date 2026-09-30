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


const resurgenceAction = {
  id: "wild-resurgence-regain-wild-shape-slot-1",
  name: "Wild Resurgence",
  actionCost: "none",
  sourceResourceId: "spell-slot-1",
  sourceCost: 1,
  additionalSourceCosts: {},
  targetResourceId: "wild-shape",
  targetGain: 1,
  targetAllowsOverflow: false,
  requiresTargetEmpty: true,
  oncePerTurn: true,
  automation: "manual",
  priority: 99,
};
const druid = {
  combatant_id: "thalen",
  state: {
    template: {
      name: "Thalen",
      ruleset: "2024",
      resources: { "spell-slot-1": 4, "wild-shape": 2 },
      resource_conversion_actions: [resurgenceAction],
      unlimited_resources: [],
    },
    resources: { "spell-slot-1": 4, "wild-shape": 0 },
    feature_last_turn_keys: {},
    action_available: true,
    bonus_action_available: true,
    reaction_available: true,
    is_dead: false,
    is_unconscious: false,
    turn_terminated: false,
  },
};
assert.equal(C.restorationAction(druid.state, "wild-shape"), null);
assert.equal(
  C.restorationAction(druid.state, "wild-shape", "1:thalen").id,
  "wild-resurgence-regain-wild-shape-slot-1",
);
const resurgenceEvent = C.resolve(2, 1, druid, resurgenceAction, "1:thalen");
assert.equal(resurgenceEvent.feature_id, resurgenceAction.id);
assert.equal(druid.state.resources["wild-shape"], 1);
assert.equal(druid.state.resources["spell-slot-1"], 3);
assert.equal(C.available(druid.state, resurgenceAction, "1:thalen"), false);


const freeAutomatic = member();
const freeAction = {
  id: "free-slot-recovery",
  name: "Free Slot Recovery",
  actionCost: "none",
  sourceResourceId: "sorcery-points",
  sourceCost: 1,
  targetResourceId: "spell-slot-1",
  targetGain: 1,
  targetAllowsOverflow: false,
  automation: "when-all-spell-slots-empty",
  priority: 50,
};
freeAutomatic.state.template.resource_conversion_actions = [freeAction];
freeAutomatic.state.template.resources["spell-slot-1"] = 3;
freeAutomatic.state.resources["spell-slot-1"] = 0;
freeAutomatic.state.resources["sorcery-points"] = 2;
const hookResult = window.IRON_PIT_BROWSER_ABILITY_HOOKS.runPhase(
  window.IRON_PIT_BROWSER_ABILITY_HOOKS.PHASES.BONUS_ACTION_WINDOW,
  {
    sequence: 20,
    round: 1,
    member: freeAutomatic,
    setup: { heroes: [freeAutomatic], monsters: [] },
    bonusActionCheckpoint: "beforeEscape",
  },
);
assert.equal(hookResult.events[0].feature_id, "free-slot-recovery");
assert.equal(hookResult.claimed, false, "a no-action conversion must not claim the Bonus Action window");
assert.equal(freeAutomatic.state.bonus_action_available, true);

console.log("Browser resource conversion regressions passed.");
