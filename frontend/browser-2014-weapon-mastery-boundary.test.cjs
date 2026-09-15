"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-weapon-mastery.js"), "utf8"),
  { filename: "browser-weapon-mastery.js" },
);

const mastery = window.IRON_PIT_BROWSER_WEAPON_MASTERY;
const mace = {
  id: "mace-attack",
  name: "Mace",
  weaponId: "mace",
  masteryProperty: "Sap",
  kind: "melee",
};

const state2024 = {
  template: {
    ruleset: "2024",
    attacks: [mace],
    weapon_masteries: ["mace"],
  },
};
assert.equal(mastery.ownsWeapon(state2024, mace), true);
assert.equal(mastery.mastered(state2024, mace), true);
assert.equal(mastery.active(state2024, mace, "Sap"), true);

const unselected = {
  template: { ruleset: "2024", attacks: [mace], weapon_masteries: [] },
};
assert.equal(mastery.ownsWeapon(unselected, mace), true);
assert.equal(mastery.active(unselected, mace, "Sap"), false);

const foreign = { ...mace, id: "axe-attack", weaponId: "axe" };
const selectedButUnowned = {
  template: { ruleset: "2024", attacks: [mace], weapon_masteries: ["axe"] },
};
assert.equal(mastery.ownsWeapon(selectedButUnowned, foreign), false);
assert.equal(mastery.mastered(selectedButUnowned, foreign), false);
assert.equal(mastery.active(selectedButUnowned, foreign, "Sap"), false);

const state2014 = {
  template: { ruleset: "2014", attacks: [mace], weapon_masteries: ["mace"] },
};
assert.equal(mastery.ownsWeapon(state2014, mace), true);
assert.equal(mastery.mastered(state2014, mace), false);
assert.equal(mastery.active(state2014, mace, "Sap"), false);

// Legacy production 2024 fixtures can omit ruleset until their generated
// artifact is migrated; ownership + assignment are still mandatory.
const legacy2024 = {
  template: { attacks: [mace], weapon_masteries: ["mace"] },
};
assert.equal(mastery.mastered(legacy2024, mace), true);

console.log("Weapon mastery ownership/ruleset boundary regressions passed.");
