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

window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_DEBUFF_COUNTERS = { movementCost: () => null };
load("browser-condition-rules.js");
load("browser-timed-conditions.js");
load("browser-failed-save-timed-effects.js");

window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "action" && state.action_available && !window.IRON_PIT_BROWSER_CONDITION_RULES.incapacitated(state),
  spend: (state, cost) => {
    if (cost === "action") state.action_available = false;
  },
};
window.IRON_PIT_BROWSER_STATE = {
  distance: () => 5,
  effectiveMaxHp: (state) => state.current_hp,
};
load("browser-condition-removal.js");

function member(id, side) {
  return {
    combatant_id: id,
    side,
    state: {
      template: {
        name: id,
        creature_type: "humanoid",
        ruleset: "2014",
        condition_removal_actions: [],
        condition_immunities: [],
      },
      current_hp: 10,
      is_alive: true,
      is_dead: false,
      is_unconscious: false,
      action_available: true,
      bonus_action_available: true,
      reaction_available: true,
      active_effect_ids: [],
      timed_effects: [],
      active_modifiers: [],
      resources: {},
    },
  };
}

const dragon = member("Brass Dragon Wyrmling", "monsters");
const helper = member("Helper", "heroes");
const sleeper = member("Sleeper", "heroes");

const action = {
  id: "sleep-breath",
  name: "Sleep Breath",
  magicalEffect: false,
};
const rider = {
  effectId: "unconscious",
  durationRounds: 10,
  expiryTiming: "source_turn_start",
  endsOnDamage: true,
  allowedRemovalActionIds: ["wake-sleeper"],
};

const applied = window.IRON_PIT_BROWSER_FAILED_SAVE_TIMED_EFFECTS.apply(
  dragon, sleeper, action, rider, 1,
);
assert.equal(applied, "unconscious");
const effect = sleeper.state.timed_effects.find((item) => item.effect_id === "unconscious");
assert.ok(effect);
assert.equal(effect.ends_on_damage, true);
assert.deepEqual(effect.allowed_removal_action_ids, ["wake-sleeper"]);
assert.equal(window.IRON_PIT_BROWSER_CONDITION_RULES.incapacitated(sleeper.state), true);
assert.equal(window.IRON_PIT_BROWSER_CONDITION_RULES.speedZero(sleeper.state), true);

const setup = { heroes: [helper, sleeper], monsters: [dragon] };
const choice = window.IRON_PIT_BROWSER_CONDITION_REMOVAL.chooseAction(helper, setup, "1:helper");
assert.ok(choice);
assert.equal(choice.action.id, "wake-sleeper");
assert.equal(choice.target, sleeper);
assert.deepEqual(choice.conditions, ["unconscious"]);

const wake = window.IRON_PIT_BROWSER_CONDITION_REMOVAL.resolve(
  1, 1, helper, sleeper, choice.action, choice.conditions, "1:helper",
);
assert.equal(wake.feature_id, "wake-sleeper");
assert.equal(helper.state.action_available, false);
assert.equal(sleeper.state.active_effect_ids.includes("unconscious"), false);
assert.equal(sleeper.state.timed_effects.some((item) => item.effect_id === "unconscious"), false);
assert.equal(window.IRON_PIT_BROWSER_CONDITION_RULES.incapacitated(sleeper.state), false);

helper.state.action_available = true;
window.IRON_PIT_BROWSER_FAILED_SAVE_TIMED_EFFECTS.apply(
  dragon, sleeper, { ...action, id: "other-unconscious-effect" },
  { ...rider, allowedRemovalActionIds: [] }, 1,
);
assert.equal(
  window.IRON_PIT_BROWSER_CONDITION_REMOVAL.chooseAction(helper, setup, "1:helper"),
  null,
  "Wake Sleeper requires the effect to explicitly authorize wake-sleeper.",
);

console.log("Browser Brass Sleep Breath uses universal timed Unconscious and Wake Sleeper action.");
