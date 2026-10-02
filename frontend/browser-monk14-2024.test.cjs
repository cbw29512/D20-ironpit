"use strict";

const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

const l13 = structuredClone(window.IRON_PIT_BROWSER_HEROES["kael-stillwater-l13"]);
const l14 = structuredClone(window.IRON_PIT_BROWSER_HEROES["kael-stillwater-l14"]);

assert.ok(l13, "generated 2024 Monk 13 card must exist");
assert.ok(l14, "generated 2024 Monk 14 card must exist");
assert.equal(l13.speed_ft, 50);
assert.equal(l14.speed_ft, 55);
assert.equal(l14.max_hp, 115);
assert.equal(l14.resources["focus-points"], 14);

assert.deepEqual(l13.saving_throw_proficiency_grants || [], []);
assert.deepEqual(l14.saving_throw_proficiency_grants, [
  {
    source_id: "disciplined-survivor",
    abilities: ["constitution", "intelligence", "wisdom", "charisma"],
  },
]);
assert.deepEqual(l14.failed_save_reroll_grants, [
  {
    source_id: "disciplined-survivor",
    source_name: "Disciplined Survivor",
    resource_id: "focus-points",
    resource_cost: 1,
  },
]);
assert.deepEqual(l14.saving_throw_bonuses, {
  strength: 6,
  dexterity: 10,
  constitution: 8,
  intelligence: 5,
  wisdom: 6,
  charisma: 5,
});

const state = {
  template: l14,
  current_hp: l14.max_hp,
  temporary_hp: 0,
  active_effect_ids: [],
  active_buff_effect_ids: [],
  timed_effects: [],
  is_dead: false,
  is_unconscious: false,
  is_alive: true,
  turn_terminated: false,
  action_available: true,
  bonus_action_available: true,
  reaction_available: true,
  resources: { ...l14.resources },
};

window.IRON_PIT_DICE = {
  values: [1, 20],
  roll() { return this.values.shift(); },
  rollMany(count) { return Array.from({ length: count }, () => this.roll()); },
};

const save = window.IRON_PIT_BROWSER_SAVES.resolveSavingThrow(state, "constitution", 20);
assert.equal(save.succeeded, true);
assert.equal(save.roll.total, 28);
assert.equal(save.roll.revisions.at(-1).source_effect_id, "disciplined-survivor");
assert.equal(save.roll.revisions.at(-1).accepted, "replacement");
assert.match(save.roll.notation, /Disciplined Survivor/);
assert.equal(state.resources["focus-points"], 13);

console.log("2024 Monk 14 Disciplined Survivor browser parity passed.");
