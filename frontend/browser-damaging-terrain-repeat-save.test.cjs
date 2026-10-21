"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(`frontend/${name}`, "utf8"), { filename: name });

window.IRON_PIT_BROWSER_GRID_GEOMETRY = {
  effectSquareSide: () => 1,
  squareAreaDistanceFt: (position, _size, hazard) => Math.abs(position.x - hazard.x) * 5,
};
load("browser-persistent-hazards.js");
let succeeds = true;
window.IRON_PIT_BROWSER_TIMED = {
  removeGroup: (state, effect) => {
    const grouped = state.timed_effects.filter((item) =>
      item.source_id === effect.source_id && item.source_effect_id === effect.source_effect_id);
    state.timed_effects = state.timed_effects.filter((item) => !grouped.includes(item));
    return grouped.map((item) => item.effect_id);
  },
};
window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE = {
  repeatSave: () => ({
    roll: { total: succeeds ? 20 : 1, rolls: [succeeds ? 20 : 1], modifier: 0 },
    succeeded: succeeds, buffs: [],
  }),
};
load("browser-source-bound-effects.js");
const SBE = window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS;
const target = {
  combatant_id: "renamed-target", side: "heroes",
  state: {
    position: { x: 0, y: 0 }, is_dead: false, is_alive: true,
    template: { name: "Renamed Target" },
    timed_effects: [
      {
        effect_id: "incapacitated", source_id: "renamed-source",
        source_effect_id: "renamed-control", repeat_save_ability: "wisdom",
        repeat_save_dc: 11, repeat_save_before_damaging_terrain: true,
        repeat_save_failure_count: 0, turn_behavior: "forced_approach_source",
      },
      { effect_id: "charmed", source_id: "renamed-source", source_effect_id: "renamed-control" },
    ],
  },
};
const setup = {
  heroes: [target], monsters: [],
  persistent_hazards: [{
    sourceSide: "monsters", expiresRound: 10, remainingDamageCapacity: 10,
    failureDamage: 5, successDamage: 0, footprintSize: "medium",
    position: { x: 1, y: 0 }, triggerRadiusFt: 0,
  }],
};
const saved = SBE.resolveDamagingTerrainRepeatSaves(1, 1, target, { x: 1, y: 0 }, setup);
assert.equal(saved.released, true);
assert.equal(saved.events[0].feature_id, "renamed-control");
assert.deepEqual(new Set(saved.events[0].removed_condition_ids), new Set(["incapacitated", "charmed"]));
assert.equal(target.state.timed_effects.length, 0);

let preEntryCalls = 0, opportunityCalls = 0;
window.IRON_PIT_BROWSER_STATE = {
  distance: (a, b) => Math.abs(a.state.position.x - b.state.position.x) * 5,
};
window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH = {};
window.IRON_PIT_BROWSER_REACTIONS = {
  resolveOpportunityAttack: () => { opportunityCalls += 1; return null; },
};
window.IRON_PIT_BROWSER_GRAPPLE = { speedIsZero: () => false };
window.IRON_PIT_BROWSER_GRID_MOVEMENT = {
  planToward: () => ({ path: [{ x: 1, y: 0 }] }),
};
window.IRON_PIT_BROWSER_GRID_MOVEMENT_SUPPORT = { movementStepCostFt: () => 5 };
window.IRON_PIT_BROWSER_GRID_REACTION_SUPPORT = {
  approachesFearSource: () => false, distanceToPosition: () => 5,
};
window.IRON_PIT_ACTION_ECONOMY = { voluntaryActivityAvailable: () => true };
window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS.resolveDamagingTerrainRepeatSaves =
  (sequence, round, mover) => {
    preEntryCalls += 1;
    assert.deepEqual(mover.state.position, { x: 0, y: 0 });
    return {
      events: [{ sequence, round_number: round, event_type: "saving_throw" }],
      sequence: sequence + 1, released: true,
    };
  };
load("browser-reaction-movement.js");
const mover = {
  combatant_id: "mover", side: "heroes",
  state: {
    position: { x: 0, y: 0 }, movement_remaining_ft: 30,
    active_effect_ids: [], template: { name: "Mover", size: "medium" },
  },
};
const source = {
  combatant_id: "source", side: "monsters",
  state: { position: { x: 3, y: 0 }, template: { name: "Source", size: "medium" } },
};
const moved = window.IRON_PIT_BROWSER_REACTION_MOVEMENT.moveToward(
  10, 1, mover, source,
  { heroes: [mover], monsters: [source], map_definition: { cell_size_ft: 5 } },
  5, "speed", { compelled: true, turnKey: "1:mover" },
);
assert.equal(preEntryCalls, 1);
assert.equal(opportunityCalls, 0);
assert.deepEqual(mover.state.position, { x: 0, y: 0 });
assert.equal(mover.state.movement_remaining_ft, 30);
assert.equal(moved.movement, null);
assert.equal(moved.events[0].event_type, "saving_throw");
console.log("Browser damaging-terrain repeat-save regressions passed.");
