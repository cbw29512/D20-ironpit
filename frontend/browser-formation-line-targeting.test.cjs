"use strict";
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

try {
  const targeting = window.IRON_PIT_BROWSER_AREA_TARGETING;
  const area = {shape: "line", origin: "self", lengthFt: 100, widthFt: 5};
  const actor = {
    combatant_id: "renamed-caster", side: "monsters",
    state: {is_alive: true, is_dead: false, current_hp: 60,
      formation_row: "front", initial_formation_row: "front"},
  };
  const member = (id, row, feet) => ({
    combatant_id: id, side: "heroes", position_ft: feet,
    state: {is_alive: true, is_dead: false, current_hp: 15,
      formation_row: row, initial_formation_row: row},
  });
  const heroes = [
    ...["f1", "f2", "f3"].map((id, i) => member(id, "front", 20 + 30*i)),
    ...["b1", "b2", "b3"].map((id, i) => member(id, "back", 100 + 30*i)),
  ];
  const setup = {arena_mode: "formation", heroes, monsters: [actor]};
  const [first] = targeting.legalPlacements(actor, setup, area, 100);
  assert.ok(first.formationOnly);
  assert.deepEqual(first.targetIds, ["f1", "b1"]);
  assert.equal(targeting.memberInPlacement(actor, heroes[0], area, first), true);
  assert.equal(targeting.memberInPlacement(actor, heroes[1], area, first), false);
  heroes[0].state.is_alive = false;
  heroes[0].state.is_dead = true;
  heroes[0].state.current_hp = 0;
  const [second] = targeting.legalPlacements(actor, setup, area, 100);
  assert.deepEqual(second.targetIds, ["f2", "b2"]);
  assert.equal(heroes[0].state.position, undefined);
  console.log("Universal formation one-lane line targeting passed.");
} catch (error) {
  console.error("Universal formation line targeting failed.", error);
  throw error;
}
