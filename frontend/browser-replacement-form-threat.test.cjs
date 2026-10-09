"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
window.IRON_PIT_BROWSER_STATE = { distance: (a, b) => Math.abs(a.position_ft - b.position_ft) };
window.IRON_PIT_BROWSER_FORMATION = {
  weaponMeanDamage: (a) => (a.diceCount || 0) * ((a.diceSize || 6) + 1) / 2 + (a.damageBonus || 0),
};
window.IRON_PIT_BROWSER_RESOURCES = {
  available: (state, id, cost = 1) => (state.resources?.[id] || 0) >= cost,
};
window.IRON_PIT_BROWSER_CONDITION_RULES = {
  incapacitated: (state) => (state.active_effect_ids || []).includes("stunned"),
};
load("browser-replacement-form-threat.js");

const attack = { id: "claw", kind: "melee", reach: 5, diceCount: 2, diceSize: 6, damageBonus: 2 };
const defender = {
  combatant_id: "caster", side: "heroes", position_ft: 0,
  state: { current_hp: 10, temporary_hp: 0 },
};
const enemy = {
  combatant_id: "enemy", side: "monsters", position_ft: 15,
  state: {
    is_alive: true, is_dead: false, current_hp: 20, resources: {},
    template: {
      speed_ft: 30, attacks: [attack], saving_throw_actions: [],
      attack_action: { id: "two-claws", slots: [
        { attackIds: ["claw"], saveActionIds: [] },
        { attackIds: ["claw"], saveActionIds: [] },
      ] },
    },
  },
};
const setup = { heroes: [defender], monsters: [enemy] };
const threat = window.IRON_PIT_BROWSER_REPLACEMENT_FORM_THREAT;
const single = 2 * ((2 * 3.5) + 2);
assert.equal(threat.singleEnemy(enemy, defender), single);
assert.equal(threat.estimate(defender, setup), single);
assert.equal(threat.mayBeLethal(10, 0, single), true);
assert.equal(threat.mayBeLethal(10, 10, single), false);
assert.equal(threat.mayBeLethal(10, 0, 0), false);
enemy.position_ft = 150;
assert.equal(threat.estimate(defender, setup), 0, "Out of reach, even after moving");
enemy.position_ft = 15;
enemy.state.active_effect_ids = ["stunned"];
assert.equal(threat.estimate(defender, setup), 0, "Incapacitated enemies are not immediate threats");
enemy.state.active_effect_ids = [];
enemy.state.is_dead = true;
assert.equal(threat.estimate(defender, setup), 0, "Dead enemies are not immediate threats");
console.log("Universal incoming printed threat parity passed.");
