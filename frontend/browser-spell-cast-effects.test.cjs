const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

global.window = global;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

load("browser-timed-conditions.js");
load("browser-spell-cast-effects.js");

const state = {
  template: {
    id: "caster-template",
    spellCastTimedResistances: [{
      id: "typed-fire-resistance",
      name: "Typed Fire Resistance",
      qualifyingDamageType: "fire",
      resistanceDamageType: "fire",
      resourceId: "points",
      resourceCost: 1,
      durationRounds: 600,
      priority: 10,
    }],
  },
  resources: { points: 2 },
  timed_effects: [],
  active_effect_ids: [],
};

const caster = { combatant_id: "caster", state };
const spell = { id: "fire-spell", damageType: "fire", damageComponents: [] };

const applied = window.IRON_PIT_BROWSER_SPELL_CAST_EFFECTS.applyTimedResistance(caster, spell, 3);
assert.equal(applied.id, "typed-fire-resistance");
assert.equal(state.resources.points, 1);
assert.equal(state.timed_effects.length, 1);
assert.deepEqual(state.timed_effects[0].owned_damage_resistances, ["fire"]);
assert.equal(state.timed_effects[0].expires_round, 603);

assert.equal(
  window.IRON_PIT_BROWSER_SPELL_CAST_EFFECTS.applyTimedResistance(caster, spell, 4),
  null,
);
assert.equal(state.resources.points, 1);

const coldSpell = { id: "cold-spell", damageType: "cold", damageComponents: [] };
assert.equal(
  window.IRON_PIT_BROWSER_SPELL_CAST_EFFECTS.applyTimedResistance(caster, coldSpell, 5),
  null,
);
assert.equal(state.resources.points, 1);

console.log("browser spell-cast effects: ok");
