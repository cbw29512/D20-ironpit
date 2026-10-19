"use strict";
// Battle ID is intentionally excluded: it is random even when dice are seeded.
// Preserve the full ordered event payload so regressions cannot disappear into a summary.
function transcript(battle, selection, seed) {
  if (!battle || !Array.isArray(battle.events) || !Number.isInteger(seed)) {
    throw new Error("Golden transcript requires a battle with events and an integer seed.");
  }
  if (!["heroes_win", "monsters_win", "draw"].includes(battle.outcome)) {
    throw new Error("Golden transcript requires a completed fight.");
  }
  return {
    schema: 1, seed, selection: structuredClone(selection),
    outcome: battle.outcome, rounds: battle.rounds,
    events: structuredClone(battle.events),
  };
}

function assertReplay(left, right) {
  const assert = require("node:assert/strict");
  assert.deepStrictEqual(left, right, "Seeded event transcript changed");
}

module.exports = { transcript, assertReplay };
