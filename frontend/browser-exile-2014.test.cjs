"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

for (const file of [
  "browser-condition-immunity.js",
  "browser-timed-conditions.js",
  "browser-ability-hooks.js",
  "browser-attack-outcome.js",
  "browser-damage-defense-rules.js",
  "browser-zero-hp.js",
  "browser-exile.js",
]) load(file);

window.IRON_PIT_DICE = {
  roll: () => 5,
  rollMany: (count) => Array.from({ length: count }, () => 5),
};

function state(name, creatureType = "humanoid") {
  return {
    template: {
      name, ruleset: "2014", creature_type: creatureType,
      damage_resistances: [], damage_immunities: [], damage_vulnerabilities: [],
      conditional_damage_defenses: [],
      resource_backed_on_hit_exile: null,
    },
    current_hp: 200, max_hp_bonus: 0, temporary_hp: 0,
    is_alive: true, is_dead: false, is_unconscious: false, is_stable: false,
    death_save_successes: 0, death_save_failures: 0,
    active_effect_ids: [], timed_effects: [], active_modifiers: [],
    resources: {}, action_available: true, bonus_action_available: true, reaction_available: true,
  };
}

const source = { combatant_id: "varek", side: "heroes", state: state("Varek") };
source.state.template.resource_backed_on_hit_exile = {
  source_id: "hurl-through-hell",
  source_name: "Hurl Through Hell",
  resource_id: "hurl-through-hell",
  resource_cost: 1,
  expiry_timing: "source_turn_end",
  duration_rounds: 1,
  return_damage_dice_count: 10,
  return_damage_dice_size: 10,
  return_damage_bonus: 0,
  return_damage_type: "psychic",
  return_damage_excluded_creature_types: ["fiend"],
};
source.state.resources["hurl-through-hell"] = 1;
const target = { combatant_id: "target", side: "monsters", state: state("Target") };
const setup = { heroes: [source], monsters: [target] };

window.IRON_PIT_BROWSER_EXILE.installAbilityHooks();
const H = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
const outcome = window.IRON_PIT_BROWSER_ATTACK_OUTCOME.create();
H.runPhase(H.PHASES.ON_HIT, {
  sequence: 1, round: 1, member: source, target, attack: { id: "staff" },
  setup, attackOutcome: outcome, events: [],
});

assert.equal(source.state.resources["hurl-through-hell"], 0);
assert.equal(window.IRON_PIT_BROWSER_EXILE.removed(target.state), true);
assert.ok(target.state.active_effect_ids.includes("banished"));
assert.equal(outcome.exileApplied.resourceRemaining, 0);

const result = H.runPhase(H.PHASES.TURN_END_LIFECYCLE, {
  sequence: 2, round: 2, member: source, setup, events: [],
});
assert.equal(result.events.length, 1);
assert.equal(window.IRON_PIT_BROWSER_EXILE.removed(target.state), false);
assert.equal(result.events[0].damage_roll.total, 50);
assert.equal(target.state.current_hp, 150);

const fiend = { combatant_id: "fiend", side: "monsters", state: state("Fiend", "fiend") };
source.state.resources["hurl-through-hell"] = 1;
const setupFiend = { heroes: [source], monsters: [fiend] };
const outcomeFiend = window.IRON_PIT_BROWSER_ATTACK_OUTCOME.create();
H.runPhase(H.PHASES.ON_HIT, {
  sequence: 1, round: 1, member: source, target: fiend, attack: { id: "staff" },
  setup: setupFiend, attackOutcome: outcomeFiend, events: [],
});
const fiendReturn = H.runPhase(H.PHASES.TURN_END_LIFECYCLE, {
  sequence: 2, round: 2, member: source, setup: setupFiend, events: [],
});
assert.equal(fiendReturn.events[0].damage_roll, null);
assert.equal(fiend.state.current_hp, 200);

console.log("2014 Hurl Through Hell universal exile browser regression passed.");
