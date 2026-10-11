"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_STATE = { effectiveMaxHp: (state) => state.template.max_hp };
window.IRON_PIT_BROWSER_CONCENTRATION = {
  endIfIncapacitated(state) { if (state.is_unconscious || state.is_dead) state.concentration = null; },
};
window.IRON_PIT_DICE = {
  queue: [3, 4],
  roll() { return this.queue.shift(); },
};
load("browser-zero-hp.js");
load("browser-start-of-turn-timed-burn.js");
const H = window.IRON_PIT_BROWSER_START_OF_TURN_TIMED_BURN;
const state = (hp = 18, kind = "character") => ({
  template: { name: "Test creature", kind, max_hp: 20, traits: [] },
  current_hp: hp, temporary_hp: 12, is_alive: true, is_dead: false,
  is_unconscious: false, is_stable: false, death_save_failures: 0,
  death_save_successes: 0, active_effect_ids: [], timed_effects: [],
  damage_taken_this_turn_by_type: { fire: 2 },
  concentration: { effect_id: "ongoing-spell" },
});
{
  const target = state();
  assert.equal(H.loseHitPoints(target, 4), 4);
  assert.equal(target.current_hp, 14);
  assert.equal(target.temporary_hp, 12);
  assert.deepEqual(target.damage_taken_this_turn_by_type, { fire: 2 });
  assert.equal(target.death_save_failures, 0);
  assert.ok(target.concentration);
}
{
  const target = state(2);
  assert.equal(H.loseHitPoints(target, 8), 2);
  assert.equal(target.current_hp, 0);
  assert.equal(target.temporary_hp, 12);
  assert.equal(target.death_save_failures, 0);
  assert.equal(target.is_unconscious, true);
  assert.equal(target.concentration, null);
}
{
  const target = state(3, "monster");
  assert.equal(H.loseHitPoints(target, 9), 3);
  assert.equal(target.is_dead, true);
}
{
  const target = state();
  target.timed_effects.push({
    effect_id: "persistent-wound", source_id: "devil-one",
    source_effect_id: "Printed Wound",
    start_of_turn_hp_loss_dice_count: 2,
    start_of_turn_hp_loss_dice_size: 10,
  });
  const member = { combatant_id: "target", state: target };
  const setup = { heroes: [member], monsters: [] };
  const output = H.resolve(1, 2, member, setup);
  assert.equal(output.events.length, 1);
  assert.equal(target.current_hp, 11);
  assert.equal(output.events[0].hp_after, 11);
  assert.match(output.events[0].description, /not damage/);
  assert.equal(target.temporary_hp, 12);
  assert.ok(target.concentration);
}
{
  const target = state();
  assert.equal(H.applyOrStackHpLoss(target, "persistent-wound", "devil-one", "Glaive", 1, 10), 1);
  assert.equal(H.applyOrStackHpLoss(target, "persistent-wound", "devil-one", "Glaive", 1, 10), 2);
  assert.equal(H.applyOrStackHpLoss(target, "persistent-wound", "devil-two", "Glaive", 1, 10), 1);
  assert.equal(target.timed_effects.length, 2);
  assert.equal(target.timed_effects[0].start_of_turn_hp_loss_dice_count, 2);
  target.timed_effects.splice(0, 1);
  assert.equal(target.timed_effects[0].source_id, "devil-two");
}
load("browser-timed-conditions.js");
{
  const target = state();
  assert.equal(H.applyOrStackHpLoss(target, "persistent-wound", "devil-one", "Glaive", 1, 10, true), 1);
  assert.equal(H.applyOrStackHpLoss(target, "persistent-wound", "devil-two", "Glaive", 1, 10, true), 1);
  target.timed_effects.push({
    effect_id: "poisoned", source_id: "devil-one", source_effect_id: "Beard",
    cannot_regain_hit_points: true,
  });
  target.active_effect_ids.push("poisoned");
  const removed = window.IRON_PIT_BROWSER_TIMED.removeOnMagicalHealing(target);
  assert.deepEqual(removed, ["persistent-wound"]);
  assert.equal(target.timed_effects.length, 1);
  assert.equal(target.timed_effects[0].effect_id, "poisoned");
  assert.ok(target.active_effect_ids.includes("poisoned"));
}
console.log("Direct HP loss, wound stacks, and magical-healing closure passed.");
