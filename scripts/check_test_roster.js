"use strict";

const fs = require("fs");
const vm = require("vm");

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function load(path) {
  vm.runInThisContext(fs.readFileSync(path, "utf8"), { filename: path });
}

try {
  global.window = global;
  global.IRON_PIT_DICE = {
    roll: (sides) => ({ 20: 10, 12: 6, 10: 5, 8: 4, 6: 3, 4: 2 }[sides] || 1),
    rollMany: (count, sides) => Array(count).fill(({ 20: 10, 12: 6, 10: 5, 8: 4, 6: 3, 4: 2 }[sides] || 1)),
  };
  global.IRON_PIT_EFFECTS = require("../frontend/preview-effects.js");
  load("frontend/preview-test-data.js");
  load("frontend/preview-barbarian.js");
  load("frontend/preview-damage.js");
  load("frontend/preview-test-engine.js");

  const roster = global.IRON_PIT_TEST_ROSTER;
  assert(Object.keys(roster.characters).length === 3, "Public test roster should expose three pregens.");
  assert(Object.keys(roster.monsters).length === 2, "Public test roster should expose two simple monsters.");
  assert(roster.characters["kara-stonefury-l1"].attacks[0].weapon.id === "greataxe", "Barbarian should use the classic Greataxe.");
  assert(!roster.monsters["srd-goblin-warrior"], "Goblin should stay out of the simple public roster.");
  assert(roster.monsters["srd-bandit"].openingDistance === 20, "Bandit should open at 20 feet.");
  assert(roster.monsters["srd-guard"].openingDistance === 5, "Guard should open in melee.");

  const bandit = global.IRON_PIT_TEST_ENGINE.buildAutomaticBattle("aldric-vane-l1", "srd-bandit");
  const guard = global.IRON_PIT_TEST_ENGINE.buildAutomaticBattle("mara-vale-l1", "srd-guard");
  const barbarian = global.IRON_PIT_TEST_ENGINE.buildAutomaticBattle("kara-stonefury-l1", "srd-guard");
  assert(bandit.battlefield.starting_distance_ft === 20, "Bandit automatic fight should start at range.");
  assert(guard.battlefield.starting_distance_ft === 5, "Guard automatic fight should start in melee.");
  assert(bandit.events.some((event) => event.event_type === "movement" && event.distance_after_ft < 20), "Bandit fight should close distance.");
  assert(bandit.events.some((event) => event.weapon_id === "handaxe"), "Aldric should use a ranged option while separated.");
  assert(bandit.events.some((event) => event.weapon_id === "longsword" || event.weapon_id === "scimitar"), "Bandit fight should reach melee weapons.");
  assert(barbarian.events.some((event) => event.feature_id === "rage"), "Barbarian should enter Rage automatically.");
  assert(barbarian.events.some((event) => event.weapon_id === "greataxe"), "Barbarian should fight with the Greataxe in melee.");

  for (const battle of [bandit, guard, barbarian]) {
    assert(!battle.events.some((event) => event.animation === "retreat"), "Public fights must never retreat.");
    assert(!battle.events.some((event) => event.event_type === "disengage"), "Public fights must never Disengage.");
    assert(battle.events.some((event) => event.event_type === "attack"), "Public fights must produce attacks.");
  }

  console.log("Selectable browser roster checks passed.");
} catch (error) {
  console.error("Selectable browser roster checks failed", error);
  process.exitCode = 1;
}
