"use strict";
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

try {
  const T = window.IRON_PIT_BROWSER_AREA_TARGETING;
  const A = window.IRON_PIT_BROWSER_AREA_SAVES;
  const shape = {shape: "cone", origin: "self", lengthFt: 15};
  const actor = {
    combatant_id: "source", side: "monsters", position_ft: 0,
    state: {
      is_alive: true, is_dead: false, current_hp: 20,
      formation_row: "front", resources: {"breath": 1},
      action_available: true, template: {name: "Renamed Source", saving_throw_actions: []},
    },
  };
  const make = (id, row, feet) => ({
    combatant_id: id, side: "heroes", position_ft: feet,
    state: {
      is_alive: true, is_dead: false, current_hp: 15,
      formation_row: row, template: {name: id, kind: "monster"},
    },
  });
  const front = ["a", "b", "c"].map((id, i) => make(id, "front", i * 50 + 200));
  const reserve = make("reserve", "back", 600);
  const setup = {arena_mode: "formation", heroes: [...front, reserve], monsters: [actor]};
  const placements = T.legalPlacements(actor, setup, shape, 15);
  assert.equal(placements.length, 1);
  assert.equal(placements[0].formationOnly, true);
  assert.deepEqual(new Set(placements[0].targetIds), new Set(["a", "b", "c"]));
  assert.ok(front.every(target => T.memberInPlacement(actor, target, shape, placements[0])));
  assert.equal(T.memberInPlacement(actor, reserve, shape, placements[0]), false);

  const action = {
    id: "breath", name: "Renamed Breath", area: shape,
    range: 15, resourceId: "breath", resourceCost: 1,
    damageDiceCount: 2, damageDiceSize: 6,
  };
  actor.state.template.saving_throw_actions = [action];
  const origSaves = window.IRON_PIT_BROWSER_SAVES;
  try {
    window.IRON_PIT_BROWSER_SAVES = {
      ...origSaves,
      legalAction: () => true,
      resolveAction: (sequence, round, source, target) => ({
        sequence, round_number: round, event_type: "saving_throw",
        actor_id: source.combatant_id, target_id: target.combatant_id,
      }),
    };
    const chosen = A.choose(actor, setup);
    assert.ok(chosen, "Source cone remains an available Action.");
    assert.deepEqual(new Set(chosen.placement.targetIds), new Set(["a", "b", "c"]));
    // Test normal legality without consuming real actions/resources.
    for (const member of front) {
      member.state.is_alive = false;
      member.state.is_dead = true;
      member.state.current_hp = 0;
    }
    assert.deepEqual(T.legalPlacements(actor, setup, shape, 15)[0].targetIds, ["reserve"]);
    assert.deepEqual(A.choose(actor, setup).placement.targetIds, ["reserve"]);
  } finally {
    window.IRON_PIT_BROWSER_SAVES = origSaves;
  }
  console.log("Formation cone/source Breath exposure and promotion passed.");
} catch (error) {
  console.error("Formation cone/source Breath regression failed.", error);
  throw error;
}
