"use strict";

const fs = require("fs");
const vm = require("vm");

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

try {
  global.window = global;
  global.IRON_PIT_DICE = {
    roll: () => 10,
    rollMany: (count) => Array(count).fill(4),
  };
  global.IRON_PIT_EFFECTS = require("../frontend/preview-effects.js");
  global.IRON_PIT_PREVIEW = {};
  vm.runInThisContext(fs.readFileSync("frontend/preview-data.js", "utf8"));
  vm.runInThisContext(fs.readFileSync("frontend/preview-engine.js", "utf8"));

  const melee = global.IRON_PIT_PREVIEW.buildBattle(5, "melee");
  const meleeAttacks = melee.events.filter((event) => event.event_type === "attack");
  assert(meleeAttacks.some((event) => event.weapon_id === "longsword"), "Melee mode should use the Fighter longsword.");
  assert(meleeAttacks.some((event) => event.weapon_id === "scimitar"), "Melee mode should use the Goblin scimitar.");
  assert(!melee.events.some((event) => event.event_type === "disengage"), "Controlled melee mode should not become a skirmish retreat.");

  const ranged = global.IRON_PIT_PREVIEW.buildBattle(20, "ranged");
  const rangedAttacks = ranged.events.filter((event) => event.event_type === "attack");
  assert(rangedAttacks.some((event) => event.weapon_id === "handaxe"), "Ranged mode should let the Fighter throw a handaxe.");
  assert(rangedAttacks.some((event) => event.weapon_id === "shortbow"), "Ranged mode should let the Goblin use its Shortbow.");
  assert(!ranged.events.some((event) => event.event_type === "disengage"), "Controlled ranged mode should not kite after melee engagement.");

  console.log("Preview arena mode checks passed.");
} catch (error) {
  console.error("Preview arena mode checks failed", error);
  process.exitCode = 1;
}
