"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
load("browser-attachments.js");
load("browser-attachment-removal.js");
const A = window.IRON_PIT_BROWSER_ATTACHMENTS;
const R = window.IRON_PIT_BROWSER_ATTACHMENT_REMOVAL;
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "action" && state.action_available,
  spend: (state) => { if (!state.action_available) throw Error("Action unavailable"); state.action_available = false; },
  voluntaryActivityAvailable: (state) => state.voluntary_turn_activity == null,
  claimActivity: (state) => { state.voluntary_turn_activity = "movement"; },
};
window.IRON_PIT_BROWSER_STATE = {
  distance: (a, b) => Math.abs(a.position_ft - b.position_ft),
};
window.IRON_PIT_BROWSER_ABILITY_CHECK_ESCAPE = { abilityCheckBonus: () => 2 };
window.IRON_PIT_BROWSER_ABILITY_CHECKS = {
  mode: () => "normal",
  resolve: (_state, _ability, roll, dc) => ({ roll, succeeded: roll.total >= dc }),
};
window.IRON_PIT_BROWSER_EXHAUSTION = { d20Modifier: () => 0 };
const member = (id, position_ft) => ({
  combatant_id: id, position_ft,
  state: {
    template: { name: id }, action_available: true, is_alive: true, is_dead: false,
    movement_remaining_ft: 30,
  },
});
const newSetup = (distance = 5, checked = false) => {
  const source = member("source", 0), victim = member("victim", distance);
  const setup = { monsters: [source], heroes: [victim], attachments: A.attach([], {
    source_id: "source", target_id: "victim", effect_id: "feed", source_name: "Printed Drain",
    damage_dice_count: 1, damage_dice_size: 4, damage_bonus: 3,
    periodic_effect_kind: "direct_hp_loss", damage_type: null,
    action_removable: true, action_removal_range_ft: 5, source_detach_movement_ft: 5,
    blocks_source_attacks: true,
    action_removal_check_ability: checked ? "strength" : null,
    action_removal_check_dc: checked ? 13 : null,
  }) };
  return { setup, source, victim };
};
{
  const { setup, source, victim } = newSetup();
  assert.equal(A.sourceAttacksBlocked(setup, source.combatant_id), true);
  assert.equal(R.removeByAction(setup, victim, "source", "feed"), true);
  assert.equal(victim.state.action_available, false);
  assert.equal(A.sourceAttacksBlocked(setup, source.combatant_id), false);
  assert.deepEqual(setup.attachments, []);
}
{
  const { setup, victim } = newSetup(10);
  const helper = member("helper", 10);
  setup.heroes.push(helper);
  assert.equal(R.removeByAction(setup, helper, "source", "feed"), false);
  assert.equal(helper.state.action_available, true);
  assert.equal(setup.attachments.length, 1);
  // The victim's own attachment remains reachable even if its stale grid token drifts.
  assert.equal(R.removeByAction(setup, victim, "source", "feed"), true);
  assert.equal(victim.state.action_available, false);
}
{
  const { setup, source } = newSetup();
  assert.equal(R.detachWithMovement(setup, source, "feed"), true);
  assert.equal(source.state.movement_remaining_ft, 25);
  assert.deepEqual(setup.attachments, []);
}
{
  const { setup, source } = newSetup();
  const event = R.resolveBlockedSource(9, 4, setup, source);
  assert.equal(event.sequence, 9);
  assert.equal(event.feature_id, "Printed Drain");
  assert.equal(event.movement_ft, 5);
  assert.equal(source.state.movement_remaining_ft, 25);
  assert.deepEqual(event.attachment_changes.map((row) => row.operation), ["detach"]);
  assert.equal(A.sourceAttacksBlocked(setup, source.combatant_id), false);
}
{
  const { setup, source } = newSetup();
  source.state.movement_remaining_ft = 0;
  assert.equal(R.detachWithMovement(setup, source, "feed"), false);
  assert.equal(setup.attachments.length, 1);
}
{
  const { setup, victim } = newSetup(5, true);
  window.IRON_PIT_BROWSER_ROLLS = { d20: () => ({ natural: 10, total: 12 }) };
  const failed = R.attemptByAction(setup, victim, "source", "feed");
  assert.equal(failed.attempted, true);
  assert.equal(failed.success, false);
  assert.equal(victim.state.action_available, false);
  assert.equal(setup.attachments.length, 1);
}
{
  const { setup, victim } = newSetup(5, true);
  window.IRON_PIT_BROWSER_ROLLS = { d20: () => ({ natural: 11, total: 13 }) };
  const passed = R.attemptByAction(setup, victim, "source", "feed");
  assert.equal(passed.attempted, true);
  assert.equal(passed.success, true);
  assert.equal(victim.state.action_available, false);
  assert.deepEqual(setup.attachments, []);
}
console.log("Attachment Action and movement detachment browser regressions passed.");
