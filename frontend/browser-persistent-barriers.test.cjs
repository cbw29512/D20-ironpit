"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(name, "utf8"), { filename: name });

window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "action" && state.action_available,
  spend: (state) => { state.action_available = false; },
};
window.IRON_PIT_BROWSER_SPELLCASTING = {
  markSlotSpellCast: (state, turnKey) => { state.slot_spell_cast_turn_key = turnKey; },
};
window.IRON_PIT_BROWSER_CONCENTRATION = {
  start: (state, sourceId, effectId, round, _states, expiresRound, slotLevel) => {
    state.concentration = {
      source_id: sourceId, effect_id: effectId, started_round: round,
      expires_round: expiresRound, slot_level: slotLevel,
    };
    return state.concentration;
  },
};

load("frontend/browser-grid-geometry.js");
load("frontend/browser-grid-barriers.js");
load("frontend/browser-persistent-barriers.js");

const action = {
  id: "wall-of-stone", name: "Wall of Stone", level: 5, actionCost: "action",
  castRangeFt: 120, concentration: true, durationRounds: 100,
  permanentAfterFullDuration: true, minSections: 10, maxSections: 10,
  sectionsMustBeContiguous: true, sectionLengthFt: 10, sectionHeightFt: 10,
  sectionThicknessInches: 6, armorClass: 15, hitPointsPerSection: 180,
  damageImmunities: ["poison", "psychic"], blocksMovement: true,
  blocksLineOfSight: true, requiredSupportMaterial: "stone",
};

const caster = {
  combatant_id: "thalen", side: "heroes",
  state: {
    position: { x: 2, y: 7 }, action_available: true,
    resources: { "spell-slot-5": 1, "natural-recovery-free-cast": 1 },
    concentration: null,
    template: {
      name: "Thalen", size: "medium",
      alternate_spell_cast_grants: [{
        source_id: "natural-recovery-wall-of-stone", source_name: "Natural Recovery",
        spell_id: "wall-of-stone", cast_level: 5,
        resource_id: "natural-recovery-free-cast", resource_cost: 1,
      }],
    },
  },
};
const target = {
  combatant_id: "target", side: "monsters",
  state: { position: { x: 20, y: 7 }, template: { name: "Target", size: "medium" } },
};
const setup = {
  heroes: [caster], monsters: [target],
  map_definition: {
    width_squares: 24, height_squares: 16, cell_size_ft: 5,
    support_materials: ["stone"],
  },
  persistent_barriers: [],
};
const panels = Array.from({ length: 10 }, (_, index) => {
  const x = 2 + index * 2;
  return [
    { first: { x, y: 4 }, second: { x, y: 5 } },
    { first: { x: x + 1, y: 4 }, second: { x: x + 1, y: 5 } },
  ];
});

const result = window.IRON_PIT_BROWSER_PERSISTENT_BARRIERS.cast(
  1, 1, caster, setup, action, panels, "1:thalen",
);
assert.equal(result.sequence, 2);
assert.equal(caster.state.resources["spell-slot-5"], 0);
assert.equal(setup.persistent_barriers.length, 1);
assert.equal(setup.persistent_barriers[0].sections.length, 10);
assert.equal(setup.persistent_barriers[0].sections[0].current_hp, 180);
assert.equal(caster.state.concentration.effect_id, "wall-of-stone");

const barrier = setup.persistent_barriers[0];
const section = barrier.sections[0];
const poison = window.IRON_PIT_BROWSER_PERSISTENT_BARRIERS.damage(
  setup, barrier.barrier_id, section.section_id, 999, "poison",
);
assert.equal(poison.immune, true);
assert.equal(poison.appliedDamage, 0);
const broken = window.IRON_PIT_BROWSER_PERSISTENT_BARRIERS.damage(
  setup, barrier.barrier_id, section.section_id, 180, "slashing",
);
assert.equal(broken.destroyed, true);
assert.equal(section.current_hp, 0);

console.log("browser persistent barrier regressions passed");
