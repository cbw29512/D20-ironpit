"use strict";
const assert = require("node:assert/strict");
const test = require("node:test");

global.window = {
  IRON_PIT_BROWSER_GRID_GEOMETRY: {
    footprintDistanceFt: (a, _size, b) => Math.hypot(a.x - b.x, a.y - b.y) * 5,
    occupiedCells: (position) => [[position.x, position.y]],
  },
  IRON_PIT_BROWSER_AREA_SHAPES: {
    cellCenterFt: (x, y) => ({ x: x * 5 + 2.5, y: y * 5 + 2.5 }),
    radiusContains: (center, point, radius) =>
      Math.hypot(center.x - point.x, center.y - point.y) <= radius,
  },
  IRON_PIT_BROWSER_DEBUFF_COUNTERS: { difficultTerrainMultiplier: () => 2 },
  IRON_PIT_BROWSER_SUPPRESSION_ZONES: { verbalBlocked: () => false },
  IRON_PIT_ACTION_ECONOMY: { available: () => true, spend: () => {} },
  IRON_PIT_BROWSER_CONCENTRATION: {
    start: (state, sourceId, effectId) => {
      state.concentration = { source_id: sourceId, effect_id: effectId };
    },
  },
  IRON_PIT_BROWSER_SAVING_THROWS: {
    resolveSavingThrow: () => ({ roll: null, succeeded: true }),
  },
  IRON_PIT_DICE: { rollMany: (count) => Array(count).fill(1) },
  IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES: {
    resolveDamage: (_state, amount) => ({ applied: amount }),
  },
  IRON_PIT_BROWSER_ATTACK: {
    applyDamage: (state, damage) => { state.current_hp -= damage; },
  },
};
require("./browser-temporary-terrain.js");
require("./browser-save-zones.js");
window.IRON_PIT_BROWSER_ROLLS = {
  modeFromSources: (advantage, disadvantage) =>
    disadvantage > advantage ? "disadvantage" : advantage > disadvantage ? "advantage" : "normal",
};
require("./browser-ability-checks.js");

function member(id, side, x) {
  return {
    combatant_id: id, side,
    state: {
      position: { x, y: 7 }, is_alive: true, is_dead: false,
      current_hp: 100, resources: { "once-a-day": 1 },
      template: { name: id, size: "medium" },
    },
  };
}

function makeSetup() {
  const caster = member("source", "heroes", 1);
  const target = member("target", "monsters", 9);
  return { caster, target, setup: {
    heroes: [caster], monsters: [target], map_definition: {},
    save_zones: [], temporary_terrain_zones: [],
  } };
}

test("generic persistent damage zone creates matching terrain and clears on lost concentration", () => {
  const { caster, target, setup } = makeSetup();
  const action = {
    id: "renamed-source-zone", name: "Another Swarm",
    level: 5, actionCost: "action", castRangeFt: 300, radiusFt: 20,
    durationRounds: 100, saveAbility: "constitution", dc: 12,
    triggers: ["appear", "enter", "end_turn"], targetPolicy: "all",
    damageDiceCount: 4, damageDiceSize: 10, damageType: "piercing",
    successDamage: "half", resourceId: "once-a-day", resourceCost: 1,
    createsDifficultTerrain: true, lightlyObscured: true,
    concentration: true,
  };
  const result = window.IRON_PIT_BROWSER_SAVE_ZONES.cast(
    1, 1, caster, setup, action, target.state.position, "1:source",
  );
  assert.equal(result.events[0].feature_id, "renamed-source-zone");
  assert.equal(target.state.current_hp, 98);
  assert.equal(caster.state.resources["once-a-day"], 0);
  assert.equal(setup.save_zones[0].lightlyObscured, true);
  const modeOptions = { member: target, setup, skill: "perception",
    reliesOnSight: true, ability: "wisdom" };
  assert.equal(window.IRON_PIT_BROWSER_ABILITY_CHECKS.mode(target.state, 0, 0, modeOptions),
    "disadvantage");
  assert.equal(window.IRON_PIT_BROWSER_ABILITY_CHECKS.mode(target.state, 0, 0,
    { ...modeOptions, reliesOnSight: false }), "normal");
  assert.equal(setup.temporary_terrain_zones.length, 1);
  assert.equal(setup.temporary_terrain_zones[0].persistent_zone_id, setup.save_zones[0].zone_id);
  assert.equal(setup.temporary_terrain_zones[0].expires_round, 101);
  assert.equal(window.IRON_PIT_BROWSER_TEMPORARY_TERRAIN.destinationIsDifficult(
    setup.temporary_terrain_zones, target, target.state.position,
  ), true);
  caster.state.concentration = null;
  window.IRON_PIT_BROWSER_SAVE_ZONES.resolveWindow(
    2, 2, target, setup, "2:target", "end_turn",
  );
  assert.equal(setup.save_zones.length, 0);
  assert.equal(setup.temporary_terrain_zones.length, 0);
  assert.equal(window.IRON_PIT_BROWSER_ABILITY_CHECKS.mode(target.state, 0, 0, modeOptions),
    "normal");
  assert.equal(action.id, "renamed-source-zone");
});

test("a zone without terrain never creates a terrain overlay", () => {
  const { caster, target, setup } = makeSetup();
  const action = {
    id: "non-terrain", name: "Non-terrain",
    level: 0, actionCost: "action", castRangeFt: 90,
    radiusFt: 10, durationRounds: 10,
    saveAbility: "wisdom", dc: 11, triggers: ["start_turn"],
    failedSaveConditionId: "poisoned",
  };
  window.IRON_PIT_BROWSER_SAVE_ZONES.cast(
    1, 1, caster, setup, action, target.state.position, "1:source",
  );
  assert.equal(setup.save_zones.length, 1);
  assert.deepEqual(setup.temporary_terrain_zones, []);
});
