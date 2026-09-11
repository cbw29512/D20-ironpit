"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
load("browser-monsters-generated.js");
load("browser-max-hp-reduction.js");
load("browser-rolls.js");
load("browser-saves.js");

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

const berserker = monsters.find((monster) => monster.name === "Berserker");
assert.ok(berserker, "Certified Berserker must be present in the generated browser roster");
assert.ok(berserker.traits.includes("bloodied-frenzy"), "Berserker must expose Bloodied Frenzy to the browser runtime");
const berserkerState = {
  template: berserker,
  current_hp: Math.floor(berserker.max_hp / 2),
  max_hp_bonus: 0,
  max_hp_reduction: 0,
  active_effect_ids: [],
};
assert.equal(window.IRON_PIT_BROWSER_ROLLS.bloodiedAttackAdvantage(berserkerState, { kind: "melee" }), 1);
assert.equal(window.IRON_PIT_BROWSER_ROLLS.bloodiedAttackAdvantage(berserkerState, { kind: "ranged" }), 1,
  "Bloodied Frenzy applies to every attack roll, not only melee attacks");
assert.equal(window.IRON_PIT_BROWSER_SAVES.saveMode(berserkerState, "wisdom"), "advantage",
  "Bloodied Frenzy applies to every saving throw");
berserkerState.current_hp = Math.floor(berserker.max_hp / 2) + 1;
assert.equal(window.IRON_PIT_BROWSER_ROLLS.bloodiedAttackAdvantage(berserkerState, { kind: "ranged" }), 0);
assert.equal(window.IRON_PIT_BROWSER_SAVES.saveMode(berserkerState, "wisdom"), "normal");

const oldFuryState = {
  template: { max_hp: 20, traits: ["bloodied-fury"] }, current_hp: 10,
  max_hp_bonus: 0, max_hp_reduction: 0, active_effect_ids: [],
};
assert.equal(window.IRON_PIT_BROWSER_ROLLS.bloodiedAttackAdvantage(oldFuryState, { kind: "melee" }), 1);
assert.equal(window.IRON_PIT_BROWSER_ROLLS.bloodiedAttackAdvantage(oldFuryState, { kind: "ranged" }), 0,
  "Existing Bloodied Fury remains melee-only");

const magicResistanceState = {
  template: { max_hp: 20, traits: [], magic_resistance: true }, current_hp: 20,
  max_hp_bonus: 0, max_hp_reduction: 0, active_effect_ids: [],
};
assert.equal(window.IRON_PIT_BROWSER_SAVES.saveMode(magicResistanceState, "wisdom", true), "advantage",
  "Magic Resistance must grant advantage against magical saving throws");
assert.equal(window.IRON_PIT_BROWSER_SAVES.saveMode(magicResistanceState, "wisdom", false), "normal",
  "Magic Resistance must not grant advantage against nonmagical saving throws");

console.log("Generated RAW-certified browser monsters expose complete saves, Bloodied Frenzy parity, and Magic Resistance save parity.");
