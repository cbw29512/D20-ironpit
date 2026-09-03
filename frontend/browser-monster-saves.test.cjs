"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-monsters-generated.js"), "utf8"));
const expected = ["charisma", "constitution", "dexterity", "intelligence", "strength", "wisdom"];
const monsters = Object.values(window.IRON_PIT_BROWSER_MONSTERS);
assert.deepEqual(window.IRON_PIT_BROWSER_MONSTERS["srd-commoner"].saving_throw_bonuses, {
  charisma: 0,
  constitution: 0,
  dexterity: 0,
  intelligence: 0,
  strength: 0,
  wisdom: 0,
}, "Certified Commoner must expose its complete SRD saving throw fingerprint");
for (const monster of monsters) {
  assert.deepEqual(Object.keys(monster.saving_throw_bonuses || {}).sort(), expected, `${monster.name} must expose all six certified saves`);
  for (const value of Object.values(monster.saving_throw_bonuses)) assert.equal(Number.isInteger(value), true, `${monster.name} saves must be integers`);
}
console.log("Generated RAW-certified browser monsters expose all six SRD saving throws.");
