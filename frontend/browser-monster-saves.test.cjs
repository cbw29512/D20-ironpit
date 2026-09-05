"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
load("browser-monsters-generated.js");
load("browser-rolls.js");
load("browser-state.js");
load("browser-attack.js");
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
const berserker = window.IRON_PIT_BROWSER_MONSTERS["srd-berserker"];
assert.ok(berserker, "Berserker must be present in the generated RAW-certified browser roster");
assert.deepEqual(berserker.attack_roll_advantage_triggers, ["attacker_bloodied"]);
assert.deepEqual(berserker.saving_throw_advantage_triggers, ["attacker_bloodied"]);
const state = window.IRON_PIT_BROWSER_STATE.buildState(berserker);
const defender = window.IRON_PIT_BROWSER_STATE.buildState(window.IRON_PIT_BROWSER_MONSTERS["srd-commoner"]);
assert.deepEqual(window.IRON_PIT_BROWSER_ATTACK.conditionSources(state, defender, 5, "defender"), { advantage: 0, disadvantage: 0 });
assert.equal(window.IRON_PIT_BROWSER_SAVES.saveMode(state, "wisdom"), "normal");
state.current_hp = 33;
assert.equal(window.IRON_PIT_BROWSER_ATTACK.conditionSources(state, defender, 5, "defender").advantage, 1);
assert.equal(window.IRON_PIT_BROWSER_SAVES.saveMode(state, "wisdom"), "advantage");
state.max_hp_bonus = 5;
state.current_hp = 35;
assert.equal(window.IRON_PIT_BROWSER_ATTACK.conditionSources(state, defender, 5, "defender").advantage, 1, "Bloodied must use effective Max HP");
assert.equal(window.IRON_PIT_BROWSER_SAVES.saveMode(state, "wisdom"), "advantage", "Save trigger must use effective Max HP");
state.active_effect_ids.push("restrained");
assert.equal(window.IRON_PIT_BROWSER_SAVES.saveMode(state, "dexterity"), "normal", "Bloodied Advantage and Restrained Disadvantage must cancel");

const magicTemplate = structuredClone(window.IRON_PIT_BROWSER_MONSTERS["srd-commoner"]);
magicTemplate.saving_throw_advantage_triggers = ["magical_effect"];
const magicState = window.IRON_PIT_BROWSER_STATE.buildState(magicTemplate);
assert.equal(window.IRON_PIT_BROWSER_SAVES.saveMode(magicState, "wisdom"), "normal", "Magic Resistance must not affect ordinary saves");
assert.equal(window.IRON_PIT_BROWSER_SAVES.saveMode(magicState, "wisdom", true), "advantage", "Magic Resistance must affect spell and magical-effect saves");

const hellHound = window.IRON_PIT_BROWSER_MONSTERS["srd-hell-hound"];
assert.ok(hellHound, "Hell Hound must be present after recharge-family certification");
const breath = hellHound.saving_throw_actions[0];
assert.deepEqual(
  { resourceId: breath.resourceId, areaSlots: breath.areaSlots, priority: breath.priority },
  { resourceId: "srd-hell-hound-fire-breath-recharge", areaSlots: 3, priority: 100 },
);
const breathState = window.IRON_PIT_BROWSER_STATE.buildState(hellHound);
breathState.resources[breath.resourceId] = 0;
let rechargeRoll = 4;
window.IRON_PIT_DICE = { roll: () => rechargeRoll };
window.IRON_PIT_BROWSER_SAVES.rechargeStart(breathState);
assert.equal(breathState.resources[breath.resourceId], 0, "Recharge 5-6 must stay spent on 4");
rechargeRoll = 5;
window.IRON_PIT_BROWSER_SAVES.rechargeStart(breathState);
assert.equal(breathState.resources[breath.resourceId], 1, "Recharge 5-6 must restore on 5");

console.log("Generated RAW-certified browser monsters expose all six SRD saves, generic save Advantage triggers, and recharge saves.");
