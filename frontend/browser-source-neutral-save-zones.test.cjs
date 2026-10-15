"use strict";
const assert = require("node:assert/strict");
const test = require("node:test");

const contexts = [], applied = [];
global.window = {
  IRON_PIT_BROWSER_GRID_GEOMETRY: {
    footprintDistanceFt: (a, _size, b) => Math.hypot(a.x - b.x, a.y - b.y) * 5,
  },
  IRON_PIT_BROWSER_SUPPRESSION_ZONES: { verbalBlocked: () => false },
  IRON_PIT_ACTION_ECONOMY: { available: () => true, spend: () => {} },
  IRON_PIT_BROWSER_SAVING_THROWS: {
    resolveSavingThrow: (_state, _ability, _dc, context) => {
      contexts.push(context);
      return { roll: null, succeeded: global.window.saveSuccess };
    },
  },
  IRON_PIT_BROWSER_TIMED: {
    apply: (_state, effect, source, options) => {
      applied.push({ effect, source, options }); return effect;
    },
  },
  saveSuccess: true,
};
require("./browser-save-zones.js");

function member(id, side) {
  return {
    combatant_id: id, side,
    state: {
      position: { x: 1, y: 7 }, is_alive: true, is_dead: false,
      current_hp: 10, resources: {},
      template: { name: id, size: "medium" },
    },
  };
}
function scenario(targetPolicy, saveContext) {
  const source = member("source", "heroes");
  const ally = member("ally", "heroes");
  const enemy = member("enemy", "monsters");
  const fight = {
    heroes: [source, ally], monsters: [enemy], map_definition: {},
    save_zones: [{
      zone_id: "zone", source_id: "source", source_side: "heroes",
      action_id: "cloud", action_name: "Any Cloud",
      position: { x: 1, y: 7 }, radius_ft: 10, expires_round: 11,
      saveAbility: "constitution", dc: 11, triggers: ["start_turn"],
      oncePerTurn: false, failedSaveConditionId: "poisoned",
      targetPolicy, saveContext,
    }],
  };
  return { fight, members: [source, ally, enemy] };
}

test("default save zones affect only enemies and remain spell effects", () => {
  contexts.length = 0;
  const { fight, members } = scenario(undefined, undefined);
  const results = members.map((actor) => window.IRON_PIT_BROWSER_SAVE_ZONES.resolveWindow(
    1, 1, actor, fight, "1:" + actor.combatant_id, "start_turn",
  ).events.length);
  assert.deepEqual(results, [0, 0, 1]);
  assert.deepEqual(contexts.map((c) => [c.magicalEffect, c.spellEffect]), [[true, true]]);
});

test("nonmagical all-target save zone affects source, allies, and enemies", () => {
  contexts.length = 0;
  const { fight, members } = scenario("all", "nonmagical");
  const results = members.map((actor) => window.IRON_PIT_BROWSER_SAVE_ZONES.resolveWindow(
    1, 1, actor, fight, "1:" + actor.combatant_id, "start_turn",
  ).events.length);
  assert.deepEqual(results, [1, 1, 1]);
  assert.deepEqual(contexts.map((c) => [c.magicalEffect, c.spellEffect]),
    [[false, false], [false, false], [false, false]]);
});

test("failed nonmagical saves retain source context when applying Poisoned", () => {
  applied.length = 0;
  window.saveSuccess = false;
  try {
    const { fight, members } = scenario("all", "nonmagical");
    const result = window.IRON_PIT_BROWSER_SAVE_ZONES.resolveWindow(
      1, 1, members[1], fight, "1:ally", "start_turn",
    );
    assert.deepEqual(result.events[0].applied_condition_ids, ["poisoned"]);
    assert.equal(applied[0].options.sourceIsMagical, false);
  } finally {
    window.saveSuccess = true;
  }
});

test("casting preserves source policy on mutable fight zone", () => {
  const { fight, members } = scenario("all", "nonmagical");
  fight.save_zones = [];
  const action = {
    id: "cloud", name: "Any Cloud", level: 0,
    actionCost: "action", castRangeFt: 0, durationRounds: 10,
    radiusFt: 10, saveAbility: "constitution", dc: 11,
    triggers: ["start_turn"], targetPolicy: "all",
    saveContext: "nonmagical",
  };
  window.IRON_PIT_BROWSER_SAVE_ZONES.cast(
    1, 1, members[0], fight, action, members[0].state.position, "1:source",
  );
  assert.equal(fight.save_zones[0].targetPolicy, "all");
  assert.equal(fight.save_zones[0].saveContext, "nonmagical");
  assert.equal(action.targetPolicy, "all");
});
