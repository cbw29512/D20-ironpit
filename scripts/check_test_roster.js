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
    roll: (sides) => ({ 20: 10, 10: 5, 8: 4, 6: 3, 4: 2 }[sides] || 1),
    rollMany: (count, sides) => Array(count).fill(({ 20: 10, 10: 5, 8: 4, 6: 3, 4: 2 }[sides] || 1)),
  };
  global.IRON_PIT_EFFECTS = require("../frontend/preview-effects.js");
  load("frontend/preview-test-data.js");
  load("frontend/preview-test-engine.js");
  load("frontend/preview-test-ambush.js");

  const roster = global.IRON_PIT_TEST_ROSTER;
  assert(Object.keys(roster.characters).length === 2, "Public test roster should expose two pregens.");
  assert(Object.keys(roster.monsters).length === 3, "Public test roster should expose three monsters.");
  assert(roster.monsters["srd-bandit"].armor_class === 12, "Bandit AC must remain 12.");
  assert(roster.monsters["srd-guard"].armor_class === 16, "Guard AC must remain 16.");
  assert(roster.monsters["srd-guard"].attacks[1].weapon.longRange === 60, "Guard thrown Spear must retain range 20/60.");
  assert(roster.monsters["srd-goblin-warrior"].openingMode === "ranged", "Goblin should choose a ranged opening.");
  assert(roster.monsters["srd-bandit"].openingMode === "ranged", "Bandit should choose a ranged opening.");
  assert(roster.monsters["srd-guard"].openingMode === "melee", "Guard should choose a melee opening.");

  const ids = Object.keys(roster.monsters);
  for (const monsterId of ids) {
    const melee = global.IRON_PIT_TEST_ENGINE.buildTestBattle("aldric-vane-l1", monsterId, "melee");
    const ranged = global.IRON_PIT_TEST_ENGINE.buildTestBattle("mara-vale-l1", monsterId, "ranged");
    assert(melee.monster.template.id === monsterId, `Melee QA selection failed for ${monsterId}.`);
    assert(ranged.monster.template.id === monsterId, `Ranged QA selection failed for ${monsterId}.`);
    assert(melee.events.some((event) => event.event_type === "attack"), `Melee QA battle produced no attacks for ${monsterId}.`);
    assert(ranged.events.some((event) => event.event_type === "attack"), `Ranged QA battle produced no attacks for ${monsterId}.`);
  }

  const goblinAuto = global.IRON_PIT_TEST_ENGINE.buildAutomaticBattle("aldric-vane-l1", "srd-goblin-warrior");
  const banditAuto = global.IRON_PIT_TEST_ENGINE.buildAutomaticBattle("mara-vale-l1", "srd-bandit");
  const guardAuto = global.IRON_PIT_TEST_ENGINE.buildAutomaticBattle("aldric-vane-l1", "srd-guard");
  assert(goblinAuto.battlefield.starting_distance_ft === 20, "Goblin automatic fight should open at range.");
  assert(banditAuto.battlefield.starting_distance_ft === 20, "Bandit automatic fight should open at range.");
  assert(guardAuto.battlefield.starting_distance_ft === 5, "Guard automatic fight should open in melee.");

  const guardRanged = global.IRON_PIT_TEST_ENGINE.buildTestBattle("aldric-vane-l1", "srd-guard", "ranged");
  assert(
    guardRanged.events.some((event) => event.actor_id === "srd-guard" && event.weapon_id === "spear" && event.animation === "projectile"),
    "Guard should still throw its Spear in controlled ranged QA mode.",
  );

  for (const monsterId of ids) {
    const ambush = global.IRON_PIT_TEST_AMBUSH.buildTestAmbush(monsterId);
    assert(ambush.monster.template.id === monsterId, `Ambush QA selection failed for ${monsterId}.`);
    assert(
      ambush.events.some((event) => event.event_type === "hide" && event.effect_changes?.some((change) => change.effect_id === "hidden")),
      `Successful Mara Hide should remain covered against ${monsterId}.`,
    );
  }

  console.log("Selectable browser roster checks passed.");
} catch (error) {
  console.error("Selectable browser roster checks failed", error);
  process.exitCode = 1;
}
