"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

window.IRON_PIT_BROWSER_STATE = {
  effectiveMaxHp: (state) => state.template.max_hp + (state.max_hp_bonus || 0),
};
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_DICE = { roll: () => 1 };
window.IRON_PIT_BROWSER_MODIFIERS = {
  savingThrowFlat: () => 0,
  applyD20Bonus: (_state, _kind, roll) => roll,
};
window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIER_RULES = {
  consumeSavingThrowModifiers: () => {},
};
window.IRON_PIT_BROWSER_ROLLS = {
  d20: (bonus) => ({ rolls: [1], selected_roll: 1, modifier: bonus, total: 1 + bonus, mode: { value: "normal" }, revisions: [] }),
  modeFromSources: () => ({ value: "normal" }),
};

load("browser-zero-hp.js");
load("browser-regeneration.js");
load("browser-save-success-override.js");
load("browser-saving-throws.js");

function monster(extra = {}) {
  return {
    template: {
      id: "troll", name: "Troll", kind: "monster", max_hp: 40,
      saving_throw_bonuses: { wisdom: 0 },
      traits: [],
      regeneration: {
        amount: 10, requires_positive_hp: false,
        suppressed_by_damage_types: ["acid", "fire"],
        survives_zero_until_turn: true, source_name: "Regeneration",
      },
      save_success_overrides: [],
      ...extra,
    },
    current_hp: 40, max_hp_bonus: 0, temporary_hp: 0,
    is_alive: true, is_dead: false, is_unconscious: false, is_stable: false,
    death_save_successes: 0, death_save_failures: 0,
    active_effect_ids: [], timed_effects: [], active_modifiers: [],
    resources: extra.resources || {},
    damage_types_taken_since_regen: [],
  };
}

{
  const state = monster();
  const outcome = window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(state, 80, false, ["slashing"]);
  assert.equal(outcome, "unconscious");
  assert.equal(state.current_hp, 0);
  assert.equal(state.is_dead, false);
  const member = { combatant_id: "troll", state };
  const events = window.IRON_PIT_BROWSER_REGENERATION.resolve(1, 2, member);
  assert.equal(state.current_hp, 10);
  assert.match(events.events[0].description, /regains 10 hit points/);
}

{
  const state = monster();
  window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(state, 8, false, ["fire"]);
  assert.equal(state.current_hp, 32);
  window.IRON_PIT_BROWSER_REGENERATION.apply(state);
  assert.equal(state.current_hp, 32);
  window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(state, 4, false, ["slashing"]);
  window.IRON_PIT_BROWSER_REGENERATION.apply(state);
  assert.equal(state.current_hp, 38);
}

{
  const state = monster();
  window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(state, 80, false, ["fire"]);
  assert.equal(state.is_dead, false);
  const result = window.IRON_PIT_BROWSER_REGENERATION.apply(state);
  assert.equal(result.died, true);
  assert.equal(state.is_dead, true);
}

{
  const state = monster({
    regeneration: null,
    save_success_overrides: [{
      source_id: "legendary-resistance", source_name: "Legendary Resistance (3/Day)",
      resource_id: "legendary-resistance", resource_cost: 1,
    }],
    resources: { "legendary-resistance": 3 },
  });
  const first = window.IRON_PIT_BROWSER_SAVING_THROWS.resolveSavingThrow(state, "wisdom", 20, {});
  assert.equal(first.succeeded, true);
  assert.equal(first.roll.outcome_override_name, "Legendary Resistance (3/Day)");
  assert.equal(first.roll.outcome_override_uses_remaining, 2);
  assert.equal(state.resources["legendary-resistance"], 2);
  state.resources["legendary-resistance"] = 0;
  const second = window.IRON_PIT_BROWSER_SAVING_THROWS.resolveSavingThrow(state, "wisdom", 20, {});
  assert.equal(second.succeeded, false);
}

console.log("Regeneration and Legendary Resistance browser parity passed.");
