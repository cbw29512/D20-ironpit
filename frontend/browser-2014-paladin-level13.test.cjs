"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

load("browser-modifiers.js");
load("browser-zero-hp-replacement.js");
load("browser-zero-hp.js");
load("browser-spell-modifiers.js");
load("browser-precombat-spells.js");

window.IRON_PIT_BROWSER_STATE = {
  grantTemporaryHp: (state, amount) => {
    state.temporary_hp = Math.max(state.temporary_hp, amount);
    return state.temporary_hp;
  },
  effectiveMaxHp: (state) => state.template.max_hp + (state.max_hp_bonus || 0),
};
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS = { endDamageSensitive: () => {} };

const deathWard = {
  id: "death-ward",
  name: "Death Ward",
  level: 4,
  actionCost: "action",
  range: 5,
  durationMinutes: 480,
  targetPolicy: "friendly",
  targetCount: 1,
  temporaryHp: 0,
  maxHpIncrease: 0,
  currentHpIncrease: 0,
  damageResistances: [],
  concentration: false,
  priority: 95,
  modifierEffects: [{
    kind: "zero-hp-replacement",
    replacementHp: 1,
    preventsInstantDeath: true,
  }],
};

const freedom = {
  id: "freedom-of-movement",
  name: "Freedom of Movement",
  level: 4,
  actionCost: "action",
  range: 5,
  durationMinutes: 60,
  targetPolicy: "friendly",
  targetCount: 1,
  damageResistances: [],
  concentration: false,
  priority: 85,
  modifierEffects: [{
    kind: "debuff-counter",
    debuffCounter: { debuff_id: "difficult-terrain", source_scope: "any", mode: "prevent", movement_cost_ft: 0 },
  }],
};

function member() {
  const state = {
    template: {
      id: "aurelia-brightshield-2014-l13",
      name: "Aurelia Brightshield",
      kind: "character",
      max_hp: 108,
      defensive_spell_actions: [freedom, deathWard],
    },
    current_hp: 108,
    max_hp_bonus: 0,
    temporary_hp: 0,
    is_alive: true,
    is_dead: false,
    is_unconscious: false,
    is_stable: false,
    action_available: true,
    death_save_successes: 0,
    death_save_failures: 0,
    active_effect_ids: [],
    active_buff_effect_ids: [],
    active_modifiers: [],
    temporary_damage_resistances: [],
    pending_zero_hp_replacement_logs: [],
    opening_buff_id: null,
    concentration: null,
    resources: { "spell-slot-4": 1 },
  };
  return { combatant_id: "aurelia", side: "heroes", position_ft: 0, state };
}

{
  const aurelia = member();
  const choice = window.IRON_PIT_BROWSER_PRECOMBAT_SPELLS.choose(aurelia);
  assert.equal(choice.spell.id, "death-ward");
  assert.equal(choice.slotLevel, 4);

  const event = window.IRON_PIT_BROWSER_PRECOMBAT_SPELLS.resolve(
    1, aurelia, [aurelia], choice.spell, choice.slotLevel, [aurelia.state],
  );

  assert.equal(aurelia.state.action_available, true);
  assert.equal(aurelia.state.resources["spell-slot-4"], 0);
  assert.equal(aurelia.state.opening_buff_id, "death-ward");
  assert.equal(aurelia.state.active_modifiers[0].kind, "zero-hp-replacement");
  assert.equal(event.feature_id, "death-ward");

  const outcome = window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(aurelia.state, 500);
  assert.equal(outcome, "zero_hp_replacement");
  assert.equal(aurelia.state.current_hp, 1);
  assert.equal(aurelia.state.active_modifiers.length, 0);
}

console.log("2014 Paladin level 13 opening Death Ward parity passed.");
