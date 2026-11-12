"use strict";

// A renamed source uses the identical shared Prone + turn-end resolver.
// This test intentionally uses no Cult Fanatic or Command runtime dispatch.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = {
  immune: (state, condition) => (state.template.condition_immunities || []).includes(condition),
};
window.IRON_PIT_BROWSER_STATE = {
  terminateTurn: (state, reason) => {
    state.turn_terminated = true;
    state.turn_termination_reason = reason;
    state.action_available = false;
    state.bonus_action_available = false;
    state.movement_remaining_ft = 0;
  },
};
load("browser-timed-conditions.js");
load("browser-ongoing-spell-control.js");

for (const id of ["command", "renamed-compulsion"]) {
  const member = {
    combatant_id: "target", position_ft: 5,
    state: {
      template: { name: "Target", ruleset: "2014", condition_immunities: [], innate_condition_ids: [] },
      active_effect_ids: ["commanded"],
      timed_effects: [{
        effect_id: "commanded", source_id: "caster", source_effect_id: id,
        expires_target_turn_count: 1, expiry_timing: "target_turn_end",
        turn_behavior: "fall_prone_end_turn",
      }],
      action_available: true, bonus_action_available: true, movement_remaining_ft: 30,
      is_dead: false, is_unconscious: false,
    },
  };
  const event = window.IRON_PIT_BROWSER_ONGOING_SPELL_CONTROL.resolveProneEndTurn(5, 1, member);
  assert.equal(event.feature_id, id);
  assert.deepEqual(event.applied_condition_ids, ["prone"]);
  assert.ok(event.description.includes("falls Prone and ends the turn"));
  assert.ok(!event.description.includes("flee"));
  assert.ok(member.state.active_effect_ids.includes("prone"));
  assert.equal(member.state.action_available, false);
  assert.equal(member.state.bonus_action_available, false);
  assert.equal(member.state.movement_remaining_ft, 0);
  assert.equal(member.position_ft, 5);

  // Only the temporary command expires; Prone remains for normal standing.
  window.IRON_PIT_BROWSER_TIMED.removeGroup(member.state, member.state.timed_effects[0]);
  assert.deepEqual(member.state.timed_effects, []);
  assert.ok(member.state.active_effect_ids.includes("prone"));
  assert.ok(!member.state.active_effect_ids.includes("commanded"));
}

const immuneMember = {
  combatant_id: "immune", state: {
    template: { name: "Immune", condition_immunities: ["prone"], innate_condition_ids: [] },
    active_effect_ids: ["commanded"], timed_effects: [{
      effect_id: "commanded", source_id: "caster", source_effect_id: "generic-word",
      turn_behavior: "fall_prone_end_turn",
    }],
    action_available: true, bonus_action_available: true, movement_remaining_ft: 30,
    is_dead: false, is_unconscious: false,
  },
};
const immuneEvent = window.IRON_PIT_BROWSER_ONGOING_SPELL_CONTROL.resolveProneEndTurn(1, 1, immuneMember);
assert.deepEqual(immuneEvent.applied_condition_ids, []);
assert.ok(!immuneMember.state.active_effect_ids.includes("prone"));
assert.equal(immuneMember.state.action_available, false);
console.log("Browser generic delayed Prone/end-turn regression passed.");
