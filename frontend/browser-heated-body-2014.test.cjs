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

const source = {
  id: "heated-body", name: "Heated Body", activationTiming: "passive",
  meleeHitRetaliation: { rangeFt: 5, diceCount: 1, diceSize: 10, damageType: "fire", onContact: true },
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
const azer = member("azer", 0, [source]);
const attacker = member("attacker", 5, [], ["fire"]);
let rolled = 0;
window.IRON_PIT_DICE = {
  rollMany: (count, size) => {
    assert.equal(count, 1); assert.equal(size, 10);
    rolled += 1;
    return [9];
  },
};
window.IRON_PIT_BROWSER_STATE = { distance: (a, b) => Math.abs(a.position_ft - b.position_ft) };
window.IRON_PIT_BROWSER_ATTACK = {
  applyDamage: (state, value) => { state.current_hp -= value; return "hit"; },
};
const P = window.IRON_PIT_BROWSER_MELEE_RETALIATION;
assert.equal(P.active(azer).action.id, "heated-body");
assert.equal(P.apply(attacker, azer, { melee: false }), 0); // Miss, ranged, and noncontact.
assert.equal(rolled, 0);
assert.equal(P.apply(attacker, azer, { melee: false, physicalContact: true }), 4);
assert.equal(attacker.state.current_hp, 96);
attacker.position_ft = 10;
assert.equal(P.apply(attacker, azer, { melee: true }), 0); // Reach beyond 5 ft.
assert.equal(rolled, 1);
attacker.position_ft = 5;
attacker.state.template.damage_immunities.push("fire");
assert.equal(P.apply(attacker, azer, { melee: true }), 0);
assert.equal(attacker.state.current_hp, 96);
assert.equal(rolled, 2);

// Existing Fire Shield remains action-activated and never triggers from contact alone.
const fireShield = member("shield", 0, [{
  id: "fire-shield", name: "Fire Shield",
  meleeHitRetaliation: { rangeFt: 5, diceCount: 2, diceSize: 8, damageType: "cold" },
}]);
assert.equal(P.active(fireShield), null);
fireShield.state.timed_effects.push({ source_effect_id: "fire-shield" });
assert.equal(P.apply(attacker, fireShield, { physicalContact: true }), 0);
assert.equal(rolled, 2);
console.log("Passive 2014 Heated Body and existing active Fire Shield remain isolated.");


// A source-owned passive and an independently active Fire Shield both trigger on one hit.
const combined = member("heated-shield", 0, [source, {
  id: "fire-shield", name: "Fire Shield",
  meleeHitRetaliation: { rangeFt: 5, diceCount: 2, diceSize: 8, damageType: "cold" },
}]);
combined.state.timed_effects.push({ source_effect_id: "fire-shield" });
const unprotected = member("opponent", 5, []);
window.IRON_PIT_DICE.rollMany = (count, size) => {
  if (count === 1 && size === 10) return [6];
  if (count === 2 && size === 8) return [3, 3];
  throw new Error("Unexpected retaliation dice");
};
assert.deepEqual(P.activeAll(combined).map(({ action }) => action.id), ["heated-body", "fire-shield"]);
assert.equal(P.apply(unprotected, combined, { melee: true }), 12);
assert.equal(unprotected.state.current_hp, 88);
assert.equal(P.apply(unprotected, combined, { physicalContact: true }), 6);
assert.equal(unprotected.state.current_hp, 82);
