"use strict";

// Runtime behavior depends on generic effect IDs, never Duergar or Enlarge.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-rolls.js"), "utf8"));

function dice(values) {
  try {
    const pending = [...values];
    window.IRON_PIT_DICE = {
      roll: (sides) => {
        const result = pending.shift();
        assert.ok(result >= 1 && result <= sides);
        return result;
      },
      rollMany: (count, sides) => Array.from(
        { length: count }, () => window.IRON_PIT_DICE.roll(sides),
      ),
    };
  } catch (error) {
    console.error("Invalid browser test dice fixture", error);
    throw error;
  }
}
const attacker = {
  template: { max_hp: 15, traits: [] }, current_hp: 15,
  active_effect_ids: [], feature_last_turn_keys: {},
};
const weapon = {
  id: "renamed-homebrew-spear", name: "Renamed Spear", kind: "melee",
  diceCount: 1, diceSize: 6, damageBonus: 2, damageType: "piercing",
  conditionalDamage: {
    trigger: "attacker_active_effect", requiredEffectId: "large-form",
    mode: "replace_weapon", diceCount: 2, diceSize: 6,
    damageBonus: 2, damageType: "piercing",
  },
};
function check(values, critical, expectedNotation, expectedTotal) {
  try {
    dice(values);
    const result = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(
      attacker, weapon, critical, "normal", "1:homebrew",
    );
    assert.deepEqual(result.components.map((item) => item.notation), [expectedNotation]);
    assert.equal(result.roll.total, expectedTotal);
  } catch (error) {
    console.error("Browser conditional active effect weapon regression failed", error);
    throw error;
  }
}
check([4], false, "1d6+2", 6);
attacker.active_effect_ids.push("large-form");
check([3, 5], false, "2d6+2", 10);
check([1, 2, 3, 4], true, "4d6+2", 12);
attacker.active_effect_ids.pop();
check([4], false, "1d6+2", 6);
weapon.conditionalDamage.requiredEffectId = "";
assert.throws(() => {
  attacker.active_effect_ids.push("large-form");
  check([4], false, "1d6+2", 6);
}, /effect ID/);
console.log("Browser active-source-effect conditional weapon damage passed.");
