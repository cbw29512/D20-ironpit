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
    roll: (sides) => ({ 20: 15, 12: 4, 8: 4, 6: 5 }[sides] || 1),
    rollMany(count, sides) { return Array(count).fill(this.roll(sides)); },
  };
  global.IRON_PIT_EFFECTS = require("../frontend/preview-effects.js");
  load("frontend/preview-test-data.js");
  load("frontend/preview-barbarian.js");
  load("frontend/preview-damage.js");
  load("frontend/preview-test-engine.js");

  const roster = global.IRON_PIT_TEST_ROSTER;
  const engine = global.IRON_PIT_TEST_ENGINE;
  const rage = global.IRON_PIT_BARBARIAN;
  const karaTemplate = roster.characters["kara-stonefury-l1"];
  const guardTemplate = roster.monsters["srd-guard"];
  const kara = {
    template: karaTemplate, hp: karaTemplate.max_hp, attackRollEffects: [], sneakUsed: false,
    rageUses: karaTemplate.rage_uses, raging: false, rageExtensionRequired: false,
  };
  const guard = {
    template: guardTemplate, hp: guardTemplate.max_hp, attackRollEffects: [], sneakUsed: false,
    rageUses: 0, raging: false, rageExtensionRequired: false,
  };
  const events = [];

  rage.beginTurn(kara, events);
  assert(kara.raging === true, "Barbarian should enter Rage automatically.");
  assert(kara.rageUses === 1, "Entering Rage should spend one of two uses.");
  assert(events[0].effect_changes[0].effect_id === "rage", "Rage must appear on the combat card.");
  assert(events[0].effect_changes[0].operation === "apply", "Rage card effect must apply.");

  const greataxe = engine.attack(kara, guard, karaTemplate.attacks[0]);
  const rageComponent = greataxe.damage_components.find((component) => component.source === "Rage");
  assert(greataxe.weapon_id === "greataxe", "Barbarian should attack with the Greataxe in melee.");
  assert(rageComponent && rageComponent.total === 2, "Rage should add exactly +2 Strength weapon damage at level 1.");
  assert(greataxe.damage_roll.total === 9, "Greataxe raw damage should include the +2 Rage bonus.");
  assert(greataxe.damage_applied === 9, "Unresisted Greataxe damage should apply in full.");
  rage.endTurn(kara, events);
  assert(kara.raging === true, "Making an attack roll should extend Rage through the turn.");

  const spear = engine.attack(guard, kara, guardTemplate.attacks[0]);
  assert(spear.damage_roll.total === 6, "Guard spear raw damage should be 6 in the deterministic preview.");
  assert(spear.damage_applied === 3, "Rage should halve piercing damage before HP changes.");
  assert(kara.hp === 12, "Kara should lose only 3 HP from the resisted 6 damage.");
  assert(/Rage resistance reduces applied damage to 3/.test(spear.description), "Battle log should explain Rage resistance.");

  console.log("Barbarian secure-preview Rage checks passed.");
} catch (error) {
  console.error("Barbarian secure-preview checks failed", error);
  process.exitCode = 1;
}
