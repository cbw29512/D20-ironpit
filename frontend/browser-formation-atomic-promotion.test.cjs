"use strict";
// Promotion is a single live formation transition; presentation does not move.
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

try {
  const rows = window.IRON_PIT_BROWSER_FORMATION_ROWS;
  const exposed = window.IRON_PIT_BROWSER_FORMATION_ENGAGEMENT;
  const member = (id, row, feet) => ({
    combatant_id: id, side: "heroes", position_ft: feet,
    state: {is_alive: true, is_dead: false, current_hp: 10,
      formation_row: row, initial_formation_row: row,
      template: {kind: "character"}},
  });
  const dead = m => {
    m.state.current_hp = 0;
    m.state.is_dead = true;
    m.state.is_alive = false;
  };

  const allBack = Array.from({length: 3}, (_, i) =>
    member(`reserve-${i}`, "back", (i + 1) * 100));
  const one = {heroes: allBack, monsters: [], arena_mode: "formation"};
  assert.ok(allBack.every(m => exposed.effectiveRow(m, one) === "front"),
    "Live exposure occurs before the turn-start sync.");
  const originalFeet = allBack.map(m => m.position_ft);
  assert.deepEqual(rows.syncFormationRows(one).map(m => m.combatant_id),
    allBack.map(m => m.combatant_id));
  assert.ok(allBack.every(m => m.state.formation_row === "front"));
  assert.ok(allBack.every(m => m.state.initial_formation_row === "back"));
  assert.deepEqual(allBack.map(m => m.position_ft), originalFeet);
  assert.deepEqual(rows.syncFormationRows(one), []);

  const front = Array.from({length: 3}, (_, i) =>
    member(`front-${i}`, "front", i * 10));
  const back = Array.from({length: 3}, (_, i) =>
    member(`back-${i}`, "back", (i + 3) * 20));
  const two = {heroes: [...front, ...back], monsters: [], arena_mode: "formation"};
  assert.deepEqual(rows.syncFormationRows(two), []);
  front.slice(0, 2).forEach(dead);
  assert.deepEqual(rows.syncFormationRows(two), []);
  dead(front[2]);
  assert.deepEqual(rows.syncFormationRows(two).map(m => m.combatant_id),
    back.map(m => m.combatant_id));
  assert.ok(back.every(m => m.state.formation_row === "front"));
  console.log("All-backline atomic promotion and living-frontline gate passed.");
} catch (error) {
  console.error("Atomic backline promotion parity failed.", error);
  throw error;
}
