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


// A real turn must run mandatory gaze-like TURN_START hooks before Grovel.
// The separate visual integration suite verifies source-specific gaze logic.
load("browser-ability-hooks.js");
const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
const phases = [];
hooks.registerAbility(hooks.PHASES.TURN_START, {
  id: "visual-start-guard", rulesets: ["2014"],
  appliesTo: () => true,
  resolve: ({ sequence, round, member }) => {
    phases.push("visual-start");
    member.state.active_effect_ids.push("frightened");
    return {
      events: [{ sequence, round_number: round, event_type: "saving_throw",
        feature_id: "visual-start-guard", applied_condition_ids: ["frightened"] }],
      sequence: sequence + 1, claimed: false,
    };
  },
});
hooks.registerAbility(hooks.PHASES.BONUS_ACTION_WINDOW, {
  id: "voluntary-bonus-guard", rulesets: ["2014"],
  appliesTo: () => true,
  resolve: ({ sequence }) => {
    phases.push("voluntary-bonus");
    return { events: [], sequence, claimed: false };
  },
});
window.IRON_PIT_BROWSER_STATE.beginTurn = () => [];
load("browser-turn.js");
const commanded = {
  combatant_id: "commanded", side: "heroes", position_ft: 0,
  state: {
    template: { name: "Commanded", ruleset: "2014",
      condition_immunities: [], innate_condition_ids: [] },
    current_hp: 10, is_dead: false, is_unconscious: false,
    action_available: true, bonus_action_available: true, movement_remaining_ft: 30,
    active_effect_ids: ["commanded"],
    timed_effects: [{
      effect_id: "commanded", source_id: "caster", source_effect_id: "renamed-order",
      turn_behavior: "fall_prone_end_turn", expiry_timing: "target_turn_end",
      expires_target_turn_count: 1,
    }],
  },
};
const opposing = {
  combatant_id: "caster", side: "monsters", position_ft: 10,
  state: { template: { name: "Caster", ruleset: "2014" } },
};
const resolved = window.IRON_PIT_BROWSER_TURN.resolveTurn(
  1, 1, commanded, { heroes: [commanded], monsters: [opposing] },
);
assert.deepEqual(resolved.events.map((event) => event.feature_id),
  ["visual-start-guard", "renamed-order"]);
assert.deepEqual(phases, ["visual-start"]);
assert.ok(commanded.state.active_effect_ids.includes("frightened"));
assert.ok(commanded.state.active_effect_ids.includes("prone"));
assert.equal(commanded.state.turn_terminated, true);
assert.equal(commanded.state.action_available, false);
assert.equal(commanded.state.bonus_action_available, false);
assert.equal(commanded.position_ft, 0);
console.log("Browser mandatory TURN_START precedes Grovel; bonus actions stay blocked.");
