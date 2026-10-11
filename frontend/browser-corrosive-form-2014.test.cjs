"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
load("browser-damage-defense-rules.js");
load("browser-melee-retaliation.js");

const action = {
  id: "corrosive-form", name: "Corrosive Form", activationTiming: "passive",
  meleeHitRetaliation: { rangeFt: 5, diceCount: 1, diceSize: 8, damageType: "acid", onContact: true },
};
const member = (name, pos, actions, resistances = [], immunities = []) => ({
  combatant_id: name, position_ft: pos,
  state: {
    template: {
      name, timed_self_buff_actions: actions, damage_resistances: resistances,
      damage_immunities: immunities, damage_vulnerabilities: [], damage_absorptions: [],
    },
    current_hp: 100, is_alive: true, is_dead: false, timed_effects: [],
    temporary_damage_resistances: [],
  },
});
const pudding = member("pudding", 0, [action]);
const attacker = member("attacker", 5, [], ["acid"]);
let rolls = 0;
window.IRON_PIT_DICE = {
  rollMany: (count, size) => {
    assert.equal(count, 1); assert.equal(size, 8);
    rolls += 1;
    return [7];
  },
};
window.IRON_PIT_BROWSER_STATE = { distance: (a, b) => Math.abs(a.position_ft - b.position_ft) };
window.IRON_PIT_BROWSER_ATTACK = {
  applyDamage: (state, amount) => { state.current_hp -= amount; return "hit"; },
};
const retaliation = window.IRON_PIT_BROWSER_MELEE_RETALIATION;
assert.equal(retaliation.active(pudding).action.id, "corrosive-form");
assert.equal(retaliation.apply(attacker, pudding, { melee: false }), 0);
assert.equal(rolls, 0);
assert.equal(retaliation.apply(attacker, pudding, { melee: true }), 3);
assert.equal(attacker.state.current_hp, 97);
assert.equal(rolls, 1);
attacker.position_ft = 10;
assert.equal(retaliation.apply(attacker, pudding, { melee: true }), 0);
assert.equal(rolls, 1);
attacker.position_ft = 5;
assert.equal(retaliation.apply(attacker, pudding, { melee: false, physicalContact: true }), 3);
assert.equal(attacker.state.current_hp, 94);
attacker.state.template.damage_immunities.push("acid");
assert.equal(retaliation.apply(attacker, pudding, { melee: true }), 0);
assert.equal(attacker.state.current_hp, 94);
assert.equal(rolls, 3);
console.log("2014 Corrosive Form reuses passive typed retaliation; equipment destruction stays out of the arena.");
