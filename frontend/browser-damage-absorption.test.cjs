const assert = require("assert");
const fs = require("fs");
const vm = require("vm");

global.window = global;
function load(name) {
  vm.runInThisContext(fs.readFileSync(__dirname + "/" + name, "utf8"), { filename: name });
}

window.IRON_PIT_ACTION_ECONOMY = { available: () => false, spend: () => {} };
window.IRON_PIT_BROWSER_TIMED = { ownsDamageResistance: () => false };
window.IRON_PIT_BROWSER_CONDITION_RULES = { has: () => false };
window.IRON_PIT_BROWSER_HEALING = {
  restore(state, amount) {
    if (state.is_dead || amount <= 0) return 0;
    const before = state.current_hp;
    state.current_hp = Math.min(state.template.max_hp, before + amount);
    return state.current_hp - before;
  },
};

load("browser-damage-defense-rules.js");

const D = window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES;
const state = {
  current_hp: 10,
  is_dead: false,
  temporary_damage_resistances: [],
  timed_effects: [],
  zone_damage_immunities: [],
  active_conditional_damage_defenses: [],
  template: {
    name: "Absorption Test",
    max_hp: 20,
    damage_immunities: ["fire"],
    damage_resistances: [],
    damage_vulnerabilities: [],
    conditional_damage_defenses: [],
    damage_absorptions: [
      { sourceId: "fire-absorption", sourceName: "Fire Absorption", damageType: "fire" },
    ],
  },
};

assert.equal(D.adjustedDamage(state, 6, "fire"), 0);
assert.equal(state.current_hp, 10, "damage estimation must not mutate HP");

let result = D.resolveDamage(state, 6, "fire");
assert.deepEqual(result, { applied: 0, healed: 6, sourceName: "Fire Absorption" });
assert.equal(state.current_hp, 16);

result = D.resolveDamage(state, 10, "fire");
assert.deepEqual(result, { applied: 0, healed: 4, sourceName: "Fire Absorption" });
assert.equal(state.current_hp, 20);

state.current_hp = 15;
result = D.resolveDamage(state, 4, "cold");
assert.deepEqual(result, { applied: 4, healed: 0, sourceName: null });
assert.equal(state.current_hp, 15);

console.log("Browser damage absorption regressions passed.");
