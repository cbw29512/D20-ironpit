"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

load("browser-monsters-generated.js");
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

load("browser-monsters-2014.js");
const goat = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-goat"];
const giantGoat = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-giant-goat"];
const mule = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-mule"];
assert.ok(goat, "2014 Goat must be certified after Sure-Footed support");
assert.ok(giantGoat, "2014 Giant Goat must be certified after Sure-Footed support");
assert.ok(mule, "2014 Mule must be certified when Beast of Burden is arena-neutral");
assert.ok(goat.traits.includes("sure-footed"));
assert.ok(giantGoat.traits.includes("sure-footed"));
assert.deepEqual(mule.traits, ["sure-footed"],
  "Mule must retain combat-relevant Sure-Footed without modeling carrying capacity");
assert.deepEqual(mule.source_trait_names, ["Beast of Burden", "Sure-Footed"],
  "Mule must preserve its exact 2014 source trait fingerprint");

window.IRON_PIT_BROWSER_ROLLS = {
  modeFromSources: (advantage = 0, disadvantage = 0) => {
    if ((advantage > 0) === (disadvantage > 0)) return "normal";
    return advantage > 0 ? "advantage" : "disadvantage";
  },
};
load("browser-saves.js");
const state = { template: goat, active_effect_ids: [] };
assert.equal(window.IRON_PIT_BROWSER_SAVES.saveMode(state, "strength", { conditionId: "prone" }), "advantage");
assert.equal(window.IRON_PIT_BROWSER_SAVES.saveMode(state, "dexterity", { conditionId: "prone" }), "advantage");
assert.equal(window.IRON_PIT_BROWSER_SAVES.saveMode(state, "strength"), "normal");
assert.equal(window.IRON_PIT_BROWSER_SAVES.saveMode(state, "constitution", { conditionId: "prone" }), "normal");

console.log("Generated monster saving throws and 2014 Sure-Footed browser parity passed.");
