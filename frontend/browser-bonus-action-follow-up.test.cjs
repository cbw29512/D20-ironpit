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

window.IRON_PIT_BROWSER_MODIFIERS = { effectiveSpeed: (state) => state.template.speed_ft };
window.IRON_PIT_BROWSER_STATE = {
  grantTemporaryHp: (state, amount) => {
    state.temporary_hp = Math.max(state.temporary_hp || 0, amount);
    return state.temporary_hp;
  },
};
window.IRON_PIT_BROWSER_DODGE = { applyEffect: (state) => state.active_effect_ids.push("dodge") };
window.IRON_PIT_DICE = { roll: () => 4 };
window.IRON_PIT_BROWSER_TACTICAL_ACTIONS = {
  grants: (member) => member.state.template.bonusTacticalActionGrants || [],
};

load("browser-bonus-action-follow-up.js");

const member = {
  combatant_id: "kael",
  state: {
    template: {
      name: "Kael Stillwater",
      speed_ft: 50,
      bonusTacticalActionGrants: [
        {
          id: "step-of-the-wind-dash",
          name: "Step of the Wind",
          effects: ["dash"],
          resourceId: null,
        },
      ],
      bonus_action_follow_up_tactical_grants: [
        {
          source_id: "fleet-step",
          source_name: "Fleet Step",
          tactical_grant_id: "step-of-the-wind-dash",
          excluded_trigger_ids: ["step-of-the-wind-dash", "step-of-the-wind-focus", "fleet-step"],
        },
      ],
    },
    bonus_action_available: false,
    movement_remaining_ft: 50,
    dash_uses_this_turn: 0,
    disengaged_this_turn: false,
    temporary_hp: 0,
    active_effect_ids: [],
    feature_last_turn_keys: {},
  },
};

{
  const event = window.IRON_PIT_BROWSER_BONUS_ACTION_FOLLOW_UP.resolve(
    1, 1, member, "martial-arts", "1:kael",
  );
  assert.ok(event);
  assert.equal(event.feature_id, "fleet-step");
  assert.equal(event.movement_ft, 50);
  assert.equal(member.state.movement_remaining_ft, 100);
  assert.equal(member.state.dash_uses_this_turn, 1);
  assert.equal(member.state.feature_last_turn_keys["fleet-step"], "1:kael");
}

{
  const duplicate = window.IRON_PIT_BROWSER_BONUS_ACTION_FOLLOW_UP.resolve(
    2, 1, member, "patient-defense-focus", "1:kael",
  );
  assert.equal(duplicate, null);
}

{
  member.state.feature_last_turn_keys = {};
  const excluded = window.IRON_PIT_BROWSER_BONUS_ACTION_FOLLOW_UP.resolve(
    3, 1, member, "step-of-the-wind-dash", "2:kael",
  );
  assert.equal(excluded, null);
}

console.log("Browser Bonus Action follow-up regressions passed.");
