"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
window.IRON_PIT_BROWSER_STATE = {
  distance: (first, second) => Math.abs(first.position_ft - second.position_ft),
};
load("browser-spell-target-groups.js");

const groups = window.IRON_PIT_BROWSER_SPELL_TARGET_GROUPS;
const [a, b, c, d] = [0, 20, 45, 75].map((position_ft, i) => ({
  combatant_id: String.fromCharCode(97 + i),
  position_ft,
  state: { current_hp: 10 },
}));
assert.equal(groups.legalGroup([a, b], 30), true);
assert.equal(groups.legalGroup([a, c], 30), false);
assert.equal(groups.legalGroup([a, b, c], 30), false);
assert.deepEqual(groups.chooseGroup([a, c, b, d], 3, 30), [a, b]);
assert.deepEqual(groups.chooseGroup([a, c, b, d], 2, null), [a, c]);
assert.deepEqual(groups.chooseGroup([a, c, b, d], 1, 30), [a]);
assert.throws(() => groups.chooseGroup([a], 0, 30), /positive/);

window.IRON_PIT_BROWSER_OFFENSE_VALUE = { saveSpell: () => 0 };
load("browser-spell-policy-support.js");
const ranked = window.IRON_PIT_BROWSER_SPELL_POLICY_SUPPORT.rankedSaveTargets;
const action = {
  id: "renamed-command", name: "Renamed Command", level: 1,
  targetCount: 1, targetCountPerSlotAbove: 1,
  maxTargetPairDistanceFt: 30,
};
assert.deepEqual(ranked([a, c, b, d], action, 3), [a, b]);

load("browser-spell-resolution-effects.js");
const caster = { combatant_id: "caster", side: "monsters", state: { template: {} } };
const victims = [a, c].map((target) => ({
  ...target, side: "heroes", state: { template: {}, current_hp: 10 },
}));
const choice = {
  action: { ...action, saveAbility: "wisdom", dc: 11, range: 60 },
  slotLevel: 1, targetIds: ["a", "c"],
};
assert.throws(
  () => window.IRON_PIT_BROWSER_SPELL_RESOLUTION_EFFECTS.resolveEffect(
    1, 1, caster, { heroes: victims, monsters: [caster] }, choice, "1:caster",
  ),
  /pairwise distance/,
);

window.IRON_PIT_ACTION_ECONOMY = {
  available: () => true,
  spend: () => { throw new Error("Cast spent action before group validation."); },
};
load("browser-spell-resolution.js");
caster.state.resources = { "spell-slot-1": 1 };
const cast = {
  ...choice,
  action: { ...choice.action, actionCost: "action" },
};
assert.throws(
  () => window.IRON_PIT_BROWSER_SPELL_RESOLUTION.resolve(
    1, 1, caster, { heroes: victims, monsters: [caster] }, cast, "1:caster",
  ),
  /pairwise distance/,
);
assert.equal(caster.state.resources["spell-slot-1"], 1);
console.log("Browser invalid spell cast leaves the spell slot untouched.");
