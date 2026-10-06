const assert = require("assert");
const fs = require("fs");
const vm = require("vm");

global.window = global;
function load(name) {
  vm.runInThisContext(fs.readFileSync(__dirname + "/" + name, "utf8"), { filename: name });
}

window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "reaction" && state.reaction_available,
  spend: (state) => { state.reaction_available = false; },
};
window.IRON_PIT_BROWSER_TIMED = {
  ownsDamageResistance: (state, type) => (state.timed_effects || [])
    .some((effect) => (effect.ownedDamageResistances || []).includes(type)),
  apply: (state, effectId, sourceId, options) => {
    const effect = {
      effect_id: effectId,
      source_id: sourceId,
      ownedDamageResistances: options.ownedDamageResistances || [],
    };
    state.timed_effects.push(effect);
    return effect;
  },
};
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
function state() {
  return {
    current_hp: 10,
    current_round: 1,
    is_dead: false,
    reaction_available: true,
    temporary_damage_resistances: [],
    timed_effects: [],
    zone_damage_immunities: [],
    active_conditional_damage_defenses: [],
    template: {
      name: "Absorption Test",
      max_hp: 20,
      damage_immunities: [],
      damage_resistances: [],
      damage_vulnerabilities: [],
      conditional_damage_defenses: [],
      damage_absorptions: [],
      incomingDamageTypeResistanceReaction: { source_id: "superior-defense", source_name: "Superior Hunter's Defense" },
    },
  };
}

let target = state();
target.template.damage_absorptions = [
  { sourceId: "fire-absorption", sourceName: "Fire Absorption", damageType: "fire" },
];

assert.equal(D.adjustedDamage(target, 6, "fire"), 0);
assert.equal(target.current_hp, 10, "damage estimation must not mutate HP");
assert.equal(target.reaction_available, true, "damage estimation must not spend reactions");

let result = D.resolveDamage(target, 6, "fire");
assert.deepEqual(result, { applied: 0, healed: 6, sourceName: "Fire Absorption" });
assert.equal(target.current_hp, 16);
assert.equal(target.reaction_available, true, "absorption must not waste the resistance reaction");

target = state();
assert.equal(D.adjustedDamage(target, 8, "fire"), 8);
assert.equal(target.reaction_available, true);

result = D.resolveDamage(target, 8, "fire");
assert.deepEqual(result, { applied: 4, healed: 0, sourceName: null });
assert.equal(target.reaction_available, false);
assert.equal(target.timed_effects.length, 1);
assert.deepEqual(target.timed_effects[0].ownedDamageResistances, ["fire"]);

target = state();
target.current_hp = 19;
target.template.damage_absorptions = [
  { sourceId: "lightning-absorption", sourceName: "Lightning Absorption", damageType: "lightning" },
];
result = D.resolveDamage(target, 10, "lightning");
assert.deepEqual(result, { applied: 0, healed: 1, sourceName: "Lightning Absorption" });
assert.equal(target.current_hp, 20);

console.log("Browser damage absorption regressions passed.");
