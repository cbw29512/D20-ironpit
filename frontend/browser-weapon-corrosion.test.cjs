"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs"), vm = require("node:vm"), path = require("node:path");
global.window = globalThis;
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-weapon-corrosion.js"), "utf8"));
const C = window.IRON_PIT_BROWSER_WEAPON_CORROSION;
const state = { weapon_corrosion_penalties: {} };
assert.equal(C.afterHit(state, "steel-1", { hit: false, nonmagicalMetal: true }), 0);
assert.equal(C.afterHit(state, "steel-1", { hit: true, nonmagicalMetal: false }), 0);
for (let hit = 1; hit <= 5; hit++) {
  assert.equal(C.afterHit(state, "steel-1", { hit: true, nonmagicalMetal: true }), -hit);
  assert.equal(C.modifier(state, "steel-1"), -hit);
  assert.equal(C.available(state, "steel-1"), hit < 5);
}
assert.equal(C.modifier(state, "steel-2"), 0, "Other weapon must stay unaffected.");
assert.equal(C.weaponDamage(state, "steel-2", 4), 4);
assert.throws(() => C.weaponDamage(state, "steel-1", 10), /Destroyed weapon/);
assert.throws(() => C.afterHit(state, "steel-1", { hit: true, nonmagicalMetal: true }), /destroyed weapon/);
assert.throws(() => C.afterHit(state, "", { hit: true, nonmagicalMetal: true }), /weapon-instance/);
const nextFight = { weapon_corrosion_penalties: {} };
assert.equal(C.modifier(nextFight, "steel-1"), 0, "Every fight starts fresh.");
const immutableCard = Object.freeze({ id: "steel-1", damageBonus: 3 });
assert.equal(immutableCard.damageBonus, 3);
console.log("Universal encounter-local weapon corrosion state checks passed.");
