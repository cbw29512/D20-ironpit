"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
window.IRON_PIT_BROWSER_STATE = {
  effectiveMaxHp: (state) => Math.max(0, state.template.max_hp - (state.max_hp_reduction || 0)),
};
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-max-hp-drain.js"), "utf8"));

const state = (maxHp, currentHp = maxHp) => ({
  template: { max_hp: maxHp }, current_hp: currentHp, max_hp_reduction: 0,
  is_alive: true, is_dead: false, is_unconscious: false, is_stable: false,
  death_save_successes: 0, death_save_failures: 0,
});
const attack = { maxHpDrain: { damageType: "necrotic", healAttacker: true, zeroMaxHpKills: true } };

let attacker = state(30, 10), defender = state(25);
let result = window.IRON_PIT_BROWSER_MAX_HP_DRAIN.resolve(attacker, defender, attack, [
  { damage_type: "piercing", applied_total: 7 }, { damage_type: "necrotic", applied_total: 4 },
]);
assert.deepEqual(result, { reduced: 4, healed: 4 });
assert.equal(defender.max_hp_reduction, 4);
assert.equal(attacker.current_hp, 14);

attacker = state(30, 10); defender = state(25);
result = window.IRON_PIT_BROWSER_MAX_HP_DRAIN.resolve(attacker, defender, attack, [{ damage_type: "necrotic", applied_total: 0 }]);
assert.deepEqual(result, { reduced: 0, healed: 0 });
assert.equal(defender.max_hp_reduction, 0);
assert.equal(attacker.current_hp, 10);

defender = state(25, 2); defender.max_hp_reduction = 23;
result = window.IRON_PIT_BROWSER_MAX_HP_DRAIN.resolve(state(30, 30), defender, attack, [{ damage_type: "necrotic", applied_total: 5 }]);
assert.equal(result.reduced, 2);
assert.equal(window.IRON_PIT_BROWSER_STATE.effectiveMaxHp(defender), 0);
assert.equal(defender.current_hp, 0);
assert.equal(defender.is_dead, true);
assert.equal(defender.is_alive, false);

console.log("2014 browser max-HP drain regressions passed.");
