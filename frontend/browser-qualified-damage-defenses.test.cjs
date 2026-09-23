"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
window.IRON_PIT_BROWSER_TIMED = { ownsDamageResistance: () => false };
window.IRON_PIT_BROWSER_CONDITION_RULES = { has: () => false };

vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-attack.js"), "utf8"),
  { filename: "browser-attack.js" },
);

const target = {
  active_effect_ids: [],
  temporary_damage_resistances: [],
  template: {
    damage_immunities: [],
    damage_resistances: [],
    damage_vulnerabilities: [],
    qualified_damage_defenses: [{
      kind: "resistance",
      damage_types: ["bludgeoning", "piercing", "slashing"],
      attack_only: true,
      magical: false,
      bypass_materials: ["adamantine"],
      source_name: "Damage Resistances",
      source_text: "test qualified resistance",
    }],
  },
};

const mundane = { magical: false, material: null };
const magical = { magical: true, material: null };
const adamantine = { magical: false, material: "adamantine" };

assert.equal(window.IRON_PIT_BROWSER_ATTACK.adjustedDamage(target, 9, "slashing", true, mundane), 4);
assert.equal(window.IRON_PIT_BROWSER_ATTACK.adjustedDamage(target, 9, "slashing", true, magical), 9);
assert.equal(window.IRON_PIT_BROWSER_ATTACK.adjustedDamage(target, 9, "slashing", true, adamantine), 9);
assert.equal(window.IRON_PIT_BROWSER_ATTACK.adjustedDamage(target, 9, "slashing"), 9);
assert.equal(window.IRON_PIT_BROWSER_ATTACK.adjustedDamage(target, 9, "fire", true, mundane), 9);

console.log("Browser qualified damage defenses are certified.");
