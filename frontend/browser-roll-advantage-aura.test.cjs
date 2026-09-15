"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
window.IRON_PIT_BROWSER_STATE = {
  distance: (a, b) => Math.abs(a.position_ft - b.position_ft),
};
window.IRON_PIT_BROWSER_SAVES = {};
window.IRON_PIT_BROWSER_TIMED = {};
window.IRON_PIT_BROWSER_ONGOING_DAMAGE = {};
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-auras.js"), "utf8"), { filename: "browser-auras.js" });

const aura = {
  id: "authority", name: "Authority", radius_ft: 10,
  target_scope: "self-and-allies", attack_roll_advantage: true,
  saving_throw_advantage: true, disabled_while_incapacitated: true,
};
const member = (id, side, position, auras = []) => ({
  combatant_id: id, side, position_ft: position,
  state: {
    is_alive: true, is_dead: false, is_unconscious: false,
    active_effect_ids: [], template: { name: id, roll_advantage_auras: auras },
  },
});
const source = member("source", "monsters", 0, [aura]);
const ally = member("ally", "monsters", 10);
const enemy = member("enemy", "heroes", 5);
const setup = { heroes: [enemy], monsters: [source, ally] };
const A = window.IRON_PIT_BROWSER_AURAS;

assert.equal(A.attackAdvantageSources(source, setup), 1, "Aura should benefit its source when self is eligible");
assert.equal(A.attackAdvantageSources(ally, setup), 1, "Aura should benefit an ally inside its radius");
assert.equal(A.savingThrowAdvantageSources(ally, setup), 1, "Aura should grant saving throw Advantage in range");
assert.equal(A.attackAdvantageSources(enemy, setup), 0, "Aura must not benefit enemies");
ally.position_ft = 15;
assert.equal(A.attackAdvantageSources(ally, setup), 0, "Aura must not extend beyond its radius");
ally.position_ft = 10;
source.state.active_effect_ids.push("incapacitated");
assert.equal(A.attackAdvantageSources(source, setup), 0, "Incapacitation must suppress the source aura");
assert.equal(A.savingThrowAdvantageSources(ally, setup), 0, "Incapacitation must suppress allied save Advantage");

console.log("Browser roll-advantage aura parity is locked.");
