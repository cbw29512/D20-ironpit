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
  distance: (a, b) => Math.abs(a.position_ft - b.position_ft),
  effectiveMaxHp: (state) => state.template.max_hp,
};
window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES = {
  resolveDamage: (state, amount, type) => ({
    applied: (state.template.damage_immunities || []).includes(type) ? 0 : amount,
  }),
};
window.IRON_PIT_BROWSER_ATTACK = {
  applyDamage(state, amount) {
    state.current_hp = Math.max(0, state.current_hp - amount);
    if (amount > 0) (state.damage_types_taken_since_regen ||= []).push("radiant");
    if (state.current_hp === 0) {
      state.is_dead = true;
      state.is_alive = false;
    }
  },
};
window.IRON_PIT_BROWSER_HEALING = {
  restore(state, amount) {
    if (state.is_dead) return 0;
    const before = state.current_hp;
    state.current_hp = Math.min(state.template.max_hp, before + amount);
    return state.current_hp - before;
  },
};
load("browser-environment-contexts.js");
load("browser-regeneration.js");
load("browser-post-hit-save-condition.js");

const sunlight = {
  source_id: "vampire-weaknesses", source_name: "Vampire Weaknesses",
  context_id: "sunlight", disadvantage_on: ["attack_rolls", "ability_checks"],
  start_turn_damage_amount: 20, start_turn_damage_type: "radiant",
};
const source = {
  combatant_id: "emitter", side: "heroes", position_ft: 0,
  state: {
    template: { name: "Synthetic Light Source", timed_self_buff_actions: [{
      id: "new-name", name: "Different Sunlight Emitter",
      emitted_environment_contexts: [{ context_id: "sunlight", radius_ft: 30 }],
    }] },
    timed_effects: [{ source_id: "emitter", source_effect_id: "new-name" }],
  },
};
const victim = {
  combatant_id: "victim", side: "monsters", position_ft: 25,
  state: {
    template: {
      name: "Synthetic Weakness Holder", max_hp: 60,
      environment_context_reactions: [sunlight],
      regeneration: {
        amount: 10, source_name: "Regeneration", requires_positive_hp: true,
        suppressed_by_damage_types: ["radiant"],
        suppressed_by_environment_contexts: ["sunlight"],
      },
    },
    timed_effects: [], current_hp: 45, damage_types_taken_since_regen: [],
    is_dead: false, is_alive: true,
  },
};
const setup = { heroes: [source], monsters: [victim] };
const E = window.IRON_PIT_BROWSER_ENVIRONMENT_CONTEXTS;
assert.equal(E.inside(victim, setup, "sunlight"), true);
assert.equal(E.disadvantageSources(victim, setup, "attack_rolls"), 1);
assert.equal(E.disadvantageSources(victim, setup, "ability_checks"), 1);
assert.equal(E.disadvantageSources(victim, setup, "saving_throws"), 0);
const phase = window.IRON_PIT_BROWSER_POST_HIT_SAVE_CONDITION.resolveStartOfTurn(
  1, 1, victim, setup,
);
assert.equal(phase.events.at(-1).feature_id, "Vampire Weaknesses");
assert.equal(victim.state.current_hp, 25, "Sunlight deals 20, without a subsequent regen heal");
assert.equal(phase.events.some((x) => x.description?.includes("does not function")), true);
victim.position_ft = 35;
assert.deepEqual(victim.state.damage_types_taken_since_regen, ["radiant"],
  "Sunlight Radiant is retained for the next Regeneration check.");
const noSun = window.IRON_PIT_BROWSER_POST_HIT_SAVE_CONDITION.resolveStartOfTurn(
  3, 2, victim, setup,
);
assert.equal(noSun.events.some((x) => x.feature_id === "Vampire Weaknesses"), false);
assert.equal(victim.state.current_hp, 25,
  "Moving out of sunlight does not undo the prior turn Radiant suppression.");
assert.deepEqual(victim.state.damage_types_taken_since_regen, [],
  "Next-turn Regeneration consumes the prior Radiant ledger once.");
const recovered = window.IRON_PIT_BROWSER_POST_HIT_SAVE_CONDITION.resolveStartOfTurn(
  noSun.sequence, 3, victim, setup,
);
assert.equal(victim.state.current_hp, 35,
  "Regeneration resumes on the later turn without a new Radiant trigger.");
assert.ok(recovered.events.some((x) => x.description?.includes("regains 10")));
assert.equal(victim.state.template.environment_context_reactions[0].source_name, "Vampire Weaknesses");

console.log("Generic source-owned sunlight damage, disadvantage and Regeneration parity passed.");
