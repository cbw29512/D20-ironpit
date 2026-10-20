"use strict";
const assert = require("node:assert/strict");
const test = require("node:test");

const applied = [];
global.window = {
  IRON_PIT_BROWSER_GRID_GEOMETRY: {
    footprintDistanceFt: (a, _size, b) => Math.max(Math.abs(a.x - b.x), Math.abs(a.y - b.y)) * 5,
  },
  IRON_PIT_BROWSER_SUPPRESSION_ZONES: { verbalBlocked: () => false },
  IRON_PIT_ACTION_ECONOMY: { available: () => true, spend: () => {} },
  IRON_PIT_BROWSER_SAVING_THROWS: {
    resolveSavingThrow: () => ({ roll: null, succeeded: false }),
  },
  IRON_PIT_BROWSER_TIMED: {
    apply: (_state, effect, _source, options) => { applied.push(options); return effect; },
  },
};
require("./browser-save-zones.js");

function member(id, side, x) {
  return { combatant_id: id, side, state: {
    position: { x, y: 7 }, is_alive: true, is_dead: false, current_hp: 10,
    resources: {}, template: { name: id, size: "medium" },
  } };
}

function scenario() {
  const source = member("source", "heroes", 5);
  const target = member("target", "monsters", 5);
  const setup = { heroes: [source], monsters: [target], map_definition: {}, save_zones: [] };
  const action = {
    id: "zone", name: "Moving Cloud", level: 0, actionCost: "action",
    castRangeFt: 0, centerOnSource: true, followsSource: true,
    radiusFt: 10, durationRounds: 10, saveAbility: "constitution", dc: 11,
    triggers: ["start_turn"], targetPolicy: "all", saveContext: "nonmagical",
    failedSaveConditionId: "poisoned", failedSaveExpiryTiming: "target_turn_start",
  };
  return { source, target, setup, action };
}

test("source-following zone moves with its owner and fails closed without source", () => {
  const { source, target, setup, action } = scenario();
  const result = window.IRON_PIT_BROWSER_SAVE_ZONES.cast(
    1, 1, source, setup, action, source.state.position, "1:source",
  );
  assert.equal(result.events.length, 1);
  const zone = setup.save_zones[0];
  assert.equal(zone.followsSource, true);
  assert.equal(window.IRON_PIT_BROWSER_SAVE_ZONES.memberInZone(target, zone, setup), true);
  assert.equal(window.IRON_PIT_BROWSER_SAVE_ZONES.memberInZone(target, zone), false);
  source.state.position = { x: 1, y: 7 };
  assert.equal(window.IRON_PIT_BROWSER_SAVE_ZONES.memberInZone(target, zone, setup), false);
  target.state.position = { x: 1, y: 7 };
  assert.equal(window.IRON_PIT_BROWSER_SAVE_ZONES.memberInZone(target, zone, setup), true);
  setup.heroes = [];
  assert.equal(window.IRON_PIT_BROWSER_SAVE_ZONES.memberInZone(target, zone, setup), false);
});

test("failed save retains source-configured next-turn expiry", () => {
  applied.length = 0;
  const { source, target, setup, action } = scenario();
  window.IRON_PIT_BROWSER_SAVE_ZONES.cast(
    1, 1, source, setup, action, source.state.position, "1:source",
  );
  const result = window.IRON_PIT_BROWSER_SAVE_ZONES.resolveWindow(
    2, 1, target, setup, "1:target", "start_turn",
  );
  assert.equal(result.events.length, 1);
  assert.deepEqual(result.events[0].applied_condition_ids, ["poisoned"]);
  assert.equal(applied[0].expiryTiming, "target_turn_start");
  assert.equal(applied[0].sourceIsMagical, false);
});

test("exhausted zone resource cannot consume an action or create a zone", () => {
  const { source, setup, action } = scenario();
  action.resourceId = "cloud-use";
  action.resourceCost = 1;
  source.state.resources = { "cloud-use": 0 };
  assert.throws(
    () => window.IRON_PIT_BROWSER_SAVE_ZONES.cast(
      1, 1, source, setup, action, source.state.position, "1:source",
    ),
    /Resource cloud-use is unavailable/,
  );
  assert.equal(setup.save_zones.length, 0);
  assert.equal(source.state.resources["cloud-use"], 0);
});
