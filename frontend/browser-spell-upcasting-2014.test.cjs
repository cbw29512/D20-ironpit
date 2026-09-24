"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

window.IRON_PIT_BROWSER_SPELLCASTING = {
  slotSpellAvailable: () => true,
};
window.IRON_PIT_BROWSER_SPELL_AREA = {};
window.IRON_PIT_ACTION_ECONOMY = {};
window.IRON_PIT_BROWSER_OFFENSE_VALUE = {};
window.IRON_PIT_BROWSER_STATE = {};
window.IRON_PIT_BROWSER_SPELL_DAMAGE_BONUS = {
  matches: () => ({ total: 0, sources: [] }),
};

load("browser-spell-policy.js");
load("browser-spell-resolution.js");

const caster = {
  combatant_id: "varek",
  state: {
    resources: {
      "spell-slot-5": 2,
      "dark-ones-own-luck": 1,
    },
  },
};
const fireball = {
  id: "fireball",
  name: "Fireball",
  level: 3,
  actionCost: "action",
  range: 150,
  areaRadius: 20,
  saveAbility: "dexterity",
  dc: 16,
  damageDiceCount: 8,
  damageDiceSize: 6,
  damageBonus: 0,
  damageType: "fire",
  damageComponents: [],
  successDamage: "half",
  upcastDicePerLevel: 1,
};

const castLevel = window.IRON_PIT_BROWSER_SPELL_POLICY.slotLevel(
  caster,
  fireball,
  "1:varek",
);
assert.equal(castLevel, 5);

const action = window.IRON_PIT_BROWSER_SPELL_RESOLUTION.saveAction(
  {
    action: fireball,
    slotLevel: castLevel,
    targetIds: [],
    placement: null,
  },
  caster.state,
);
assert.equal(action.damageDiceCount, 10);
assert.equal(action.damageDiceSize, 6);
assert.equal(action.damageType, "fire");

console.log("Browser 2014 Pact Magic preserves printed spell level and upcasts from the selected slot.");
