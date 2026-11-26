"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), {filename: name},
);
for (const filename of [
  "browser-condition-immunity.js", "browser-timed-conditions.js",
  "browser-ability-hooks.js", "browser-attack-outcome.js",
  "browser-damage-defense-rules.js", "browser-zero-hp.js", "browser-exile.js",
]) load(filename);

window.IRON_PIT_DICE = {
  roll: () => 5,
  rollMany: (count) => Array.from({length: count}, () => 5),
};
window.IRON_PIT_BROWSER_SAVING_THROWS = {
  resolveSavingThrow: () => ({succeeded: false}),
};
const state = (name) => ({
  template: {
    name, ruleset: "2024", creature_type: "humanoid",
    damage_resistances: [], damage_immunities: [], damage_vulnerabilities: [],
    conditional_damage_defenses: [], damage_absorptions: [],
  },
  current_hp: 200, max_hp_bonus: 0, temporary_hp: 0,
  is_alive: true, is_dead: false, is_unconscious: false, is_stable: false,
  death_save_successes: 0, death_save_failures: 0,
  active_effect_ids: [], timed_effects: [], active_modifiers: [],
  resources: {}, action_available: true, bonus_action_available: true,
  reaction_available: true,
});
const attacker = {combatant_id: "caster", side: "heroes", state: state("Varek")};
attacker.state.template.resource_backed_on_hit_exile = {
  source_id: "hurl-through-hell", source_name: "Hurl Through Hell",
  resource_id: "hurl-through-hell", resource_cost: 1,
  once_per_turn: true, save_ability: "charisma", save_dc: 17,
  expiry_timing: "source_turn_end", duration_rounds: 1,
  hit_damage_dice_count: 8, hit_damage_dice_size: 10,
  hit_damage_type: "psychic",
  hit_damage_excluded_creature_types: ["fiend"],
  apply_condition_ids: ["incapacitated"],
};
attacker.state.resources["hurl-through-hell"] = 1;
const victim = {combatant_id: "victim", side: "monsters", state: state("Target")};
const setup = {heroes: [attacker], monsters: [victim]};
window.IRON_PIT_BROWSER_EXILE.installAbilityHooks();
const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
const outcome = window.IRON_PIT_BROWSER_ATTACK_OUTCOME.create();
hooks.runPhase(hooks.PHASES.ON_HIT, {
  sequence: 1, round: 1, member: attacker, target: victim, setup,
  attackOutcome: outcome, turnKey: "1:caster", events: [],
});
assert.equal(attacker.state.resources["hurl-through-hell"], 0);
assert.ok(victim.state.active_effect_ids.includes("hurl-through-hell"));
assert.ok(victim.state.active_effect_ids.includes("incapacitated"));
assert.equal(window.IRON_PIT_BROWSER_EXILE.removed(victim.state), false);
assert.equal(window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES.adjustedDamage(victim.state, 21, "acid"), 0);
assert.equal(window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES.resolveDamage(victim.state, 21, "fire").applied, 0);
assert.equal(victim.state.current_hp, 200);
const early = hooks.runPhase(hooks.PHASES.TURN_END_LIFECYCLE, {
  sequence: 2, round: 1, member: attacker, setup, events: [],
});
assert.equal(early.events.length, 0);
const returned = hooks.runPhase(hooks.PHASES.TURN_END_LIFECYCLE, {
  sequence: 2, round: 2, member: attacker, setup, events: [],
});
assert.equal(returned.events.length, 1);
assert.equal(returned.events[0].damage_roll.total, 40);
assert.equal(victim.state.current_hp, 160);
assert.ok(!victim.state.active_effect_ids.includes("hurl-through-hell"));
assert.ok(!victim.state.active_effect_ids.includes("incapacitated"));
assert.ok(!victim.state.timed_effects.some((e) => e.all_damage_immunity));
console.log("2024 Hurl Through Hell: in-arena timed immunity and delayed 8d10 passed.");
