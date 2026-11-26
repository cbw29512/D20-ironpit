"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
window.IRON_PIT_BROWSER_BREATHING = { reset: (state) => {
  state.breath_hold_rounds_remaining = null;
  state.breath_survival_rounds_remaining = null;
  state.suffocating_at_zero = false;
} };
window.IRON_PIT_BROWSER_STATE = {
  sizeAtMost: (member, maximum) => {
    const rank = { tiny: 0, small: 1, medium: 2, large: 3, huge: 4, gargantuan: 5 };
    return rank[member.state.template.size] <= rank[maximum];
  },
};
load("browser-attachments.js");
const A = window.IRON_PIT_BROWSER_ATTACHMENTS;

const member = (id, side, size, position = 0) => ({
  combatant_id: id, side, position_ft: position,
  state: {
    template: { name: id, size, innate_condition_ids: [] },
    is_alive: true, is_dead: false, active_effect_ids: [], timed_effects: [],
    grapple_sources: [], attachment_blind_source_ids: [],
    attachment_breathing_source_ids: [], attachment_speed_zero_source_ids: [],
  },
});
const spec = {
  effect_id: "head-attachment", source_name: "Printed Attack",
  periodic_effect_kind: null, dice_count: 0, dice_size: 6,
  damage_bonus: 0, damage_type: null, tick_timing: "source_turn_start",
  action_removable: true, action_removal_range_ft: 5, source_detach_movement_ft: 5,
  attach_max_target_size: "large", enhanced_on_attack_advantage: true,
  enhanced_max_target_size: "medium", source_target_lock: true,
  source_advantage_against_target: true, source_speed_zero: true,
  moves_with_target: true, enhanced_blinds_target: true,
  enhanced_prevents_breathing: true, action_removal_check_ability: "strength",
  action_removal_check_dc: 13,
};

{
  const source = member("source", "monsters", "small"), target = member("target", "heroes", "medium", 5);
  const other = member("other", "heroes", "medium", 5);
  const setup = { monsters: [source], heroes: [target, other], attachments: [] };
  assert.equal(A.applyOnHit(setup, source, target, { onHitAttachment: spec }, "advantage"), true);
  assert.equal(setup.attachments[0].blinds_target, true);
  assert.deepEqual(target.state.attachment_breathing_source_ids, ["source"]);
  assert.ok(target.state.active_effect_ids.includes("blinded"));
  assert.deepEqual(source.state.attachment_speed_zero_source_ids, ["head-attachment"]);
  assert.equal(A.sourceAttacksBlocked(setup, "source", "other"), true);
  assert.equal(A.sourceAttacksBlocked(setup, "source", "target"), false);
  assert.equal(A.attackAdvantage(setup, "source", "target"), 1);
  target.position_ft = 30; A.moveWithTarget(setup, "target");
  assert.equal(source.position_ft, 30);
  setup.attachments = A.detach(setup.attachments, "source", "head-attachment");
  A.syncControls(setup);
  assert.equal(target.state.active_effect_ids.includes("blinded"), false);
  assert.deepEqual(target.state.attachment_breathing_source_ids, []);
}

{
  const source = member("source", "monsters", "small"), target = member("target", "heroes", "large", 5);
  const setup = { monsters: [source], heroes: [target], attachments: [] };
  assert.equal(A.applyOnHit(setup, source, target, { onHitAttachment: spec }, "advantage"), true);
  assert.equal(setup.attachments[0].blinds_target, false, "Large attaches but does not meet Medium head qualifier");
}

{
  const source = member("source", "monsters", "small"), target = member("target", "heroes", "huge", 5);
  const setup = { monsters: [source], heroes: [target], attachments: [] };
  assert.equal(A.applyOnHit(setup, source, target, { onHitAttachment: spec }, "advantage"), false);
}

console.log("Conditional control attachment browser parity passed.");
