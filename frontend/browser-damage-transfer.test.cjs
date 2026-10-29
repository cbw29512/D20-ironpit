const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = {};
vm.runInThisContext(fs.readFileSync(`${__dirname}/browser-damage-transfer.js`, "utf8"));

const calls = [];
window.IRON_PIT_BROWSER_ZERO_HP = {
  applyDamage: (...args) => { calls.push(args); return "damaged"; },
};

function member(id, rule = null) {
  return {
    combatant_id: id,
    state: {
      template: { name: id, damage_transfer: rule },
      current_hp: 20, is_alive: true, is_dead: false, grapple_sources: [],
    },
  };
}

const rule = {
  source_name: "Renamed Shared Harm", relation: "source_grapples_target",
  source_rounding: "down", transferred_damage_retriggers: false,
};
const owner = member("owner", rule);
const victim = member("victim");
victim.state.grapple_sources.push({ source_id: "owner", escape_dc: 13 });
const setup = { heroes: [victim], monsters: [owner] };
assert.deepEqual(window.IRON_PIT_BROWSER_DAMAGE_TRANSFER.resolveForState(owner.state, 9, setup), {
  amount: 4, damageComponents: [],
});
assert.equal(calls.length, 1);
assert.equal(calls[0][0], victim.state);
assert.equal(calls[0][1], 5);
assert.equal(calls[0][7], false, "transferred damage cannot recursively transfer");

victim.state.grapple_sources = [];
assert.deepEqual(window.IRON_PIT_BROWSER_DAMAGE_TRANSFER.resolveForState(owner.state, 9, setup), {
  amount: 9, damageComponents: [],
});
assert.equal(calls.length, 1);
victim.state.grapple_sources.push({ source_id: "owner", escape_dc: 13 });
const components = [
  { damage_type: "fire", applied_total: 5 },
  { damage_type: "cold", applied_total: 5 },
];
assert.deepEqual(window.IRON_PIT_BROWSER_DAMAGE_TRANSFER.resolveForState(
  owner.state, 10, setup, ["fire", "cold"], components,
), {
  amount: 5,
  damageComponents: [
    { damage_type: "fire", applied_total: 3 },
    { damage_type: "cold", applied_total: 2 },
  ],
});
assert.deepEqual(calls[1][6], [
  { damage_type: "fire", applied_total: 2 },
  { damage_type: "cold", applied_total: 3 },
]);
assert.deepEqual(components.map((item) => item.applied_total), [5, 5]);
const originalError = console.error;
console.error = () => {};
assert.throws(
  () => window.IRON_PIT_BROWSER_DAMAGE_TRANSFER.resolveForState(owner.state, 9, null),
  /encounter setup/,
);
console.error = originalError;

console.log("Browser source-neutral Damage Transfer regressions passed.");
