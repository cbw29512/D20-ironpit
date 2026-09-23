"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

load("browser-heroes.js");
load("browser-condition-rules.js");
load("browser-action-economy.js");
load("browser-d20-test-override.js");
load("browser-ability-checks.js");
load("browser-initiative.js");
load("browser-rogue-defenses.js");

const heroes = Object.values(window.IRON_PIT_BROWSER_HEROES);
const rogue2 = heroes.find((hero) => hero.id === "mara-quickstep-2014-l2");
const rogue5 = heroes.find((hero) => hero.id === "mara-quickstep-2014-l5");
const rogue7 = heroes.find((hero) => hero.id === "mara-quickstep-2014-l7");
const rogue10 = heroes.find((hero) => hero.id === "mara-quickstep-2014-l10");
const rogue11 = heroes.find((hero) => hero.id === "mara-quickstep-2014-l11");
const rogue12 = heroes.find((hero) => hero.id === "mara-quickstep-2014-l12");
const rogue15 = heroes.find((hero) => hero.id === "mara-quickstep-2014-l15");
const rogue16 = heroes.find((hero) => hero.id === "mara-quickstep-2014-l16");
const rogue17 = heroes.find((hero) => hero.id === "mara-quickstep-2014-l17");
const rogue18 = heroes.find((hero) => hero.id === "mara-quickstep-2014-l18");
const rogue19 = heroes.find((hero) => hero.id === "mara-quickstep-2014-l19");
const rogue20 = heroes.find((hero) => hero.id === "mara-quickstep-2014-l20");
const rogue2024_17 = heroes.find((hero) => hero.id === "mara-quickstep-l17");
assert.ok(rogue2 && rogue5 && rogue7 && rogue10 && rogue11 && rogue12 && rogue15 && rogue16 && rogue17 && rogue18 && rogue19 && rogue20 && rogue2024_17);
assert.equal(rogue2.ruleset, "2014");
assert.equal(rogue2.cunning_action, true);
assert.equal(rogue5.uncanny_dodge, true);
assert.equal(rogue7.evasion, true);
assert.equal(rogue10.sneak_attack_d6, 5);
assert.equal(rogue11.ruleset, "2014");
assert.equal(rogue11.sneak_attack_d6, 6);
assert.deepEqual(rogue11.weapon_masteries, []);
assert.ok(rogue11.attacks.every((attack) => attack.masteryProperty == null));
assert.equal(rogue12.ability_scores.constitution, 16);
assert.equal(rogue15.saving_throw_bonuses.wisdom, 7);
assert.equal(rogue16.ability_scores.constitution, 18);
assert.deepEqual(rogue17.first_round_extra_turn_grants, [
  { source_id: "thiefs-reflexes", source_name: "Thief's Reflexes", initiative_offset: -10 },
]);
assert.deepEqual(rogue2024_17.first_round_extra_turn_grants, rogue17.first_round_extra_turn_grants);
assert.equal(rogue18.suppress_attack_advantage_while_not_incapacitated, true);
assert.equal(rogue19.ability_scores.constitution, 20);
assert.equal(rogue20.miss_to_hit_override_resource_id, "stroke-of-luck");
assert.equal(rogue20.miss_to_hit_override_source_name, "Stroke of Luck");
assert.equal(rogue20.resources["stroke-of-luck"], 1);
assert.deepEqual(rogue20.failed_d20_test_override_grants, [{
  source_id: "stroke-of-luck",
  source_name: "Stroke of Luck",
  resource_id: "stroke-of-luck",
  replacement_roll: 20,
  test_kinds: ["ability_check"],
}]);

const luckyCheckState = {
  template: rogue20,
  resources: { ...rogue20.resources },
};
const failedCheck = {
  notation: "1 + 17", rolls: [1], selected_roll: 1,
  modifier: 17, total: 18, mode: "normal", revisions: [],
};
const luckyCheck = window.IRON_PIT_BROWSER_ABILITY_CHECKS.resolve(
  luckyCheckState, "dexterity", failedCheck, 25,
);
assert.equal(luckyCheck.succeeded, true);
assert.equal(luckyCheck.roll.selected_roll, 20);
assert.equal(luckyCheck.roll.total, 37);
assert.equal(luckyCheck.roll.revisions.at(-1).source_effect_id, "stroke-of-luck");
assert.equal(luckyCheckState.resources["stroke-of-luck"], 0);

const scheduledMembers = [
  { combatant_id: "mara17", state: { template: rogue17 } },
  { combatant_id: "target17", state: { template: {} } },
];
const scheduledGroups = [
  { members: [scheduledMembers[0]], combatant_ids: ["mara17"], natural_roll: 15, initiative_count: 20, tie_break_rolls: [] },
  { members: [scheduledMembers[1]], combatant_ids: ["target17"], natural_roll: 12, initiative_count: 17, tie_break_rolls: [] },
];
const firstRound = window.IRON_PIT_BROWSER_INITIATIVE.firstRoundSchedule(scheduledGroups);
assert.deepEqual(firstRound.order, ["mara17", "target17", "mara17"]);
assert.deepEqual(firstRound.extras, [{
  combatant_id: "mara17",
  initiative_count: 10,
  source_id: "thiefs-reflexes",
  source_name: "Thief's Reflexes",
}]);
const scheduledInitiative = {
  turn_order: ["mara17", "target17"],
  first_round_turn_order: firstRound.order,
  first_round_extra_turns: firstRound.extras,
};
assert.deepEqual(
  window.IRON_PIT_BROWSER_INITIATIVE.turnOrderForRound(1, scheduledInitiative, scheduledMembers),
  ["mara17", "target17", "mara17"],
);
assert.deepEqual(
  window.IRON_PIT_BROWSER_INITIATIVE.turnOrderForRound(2, scheduledInitiative, scheduledMembers),
  ["mara17", "target17"],
);

const naturalTwentyGroups = [
  { members: [scheduledMembers[0]], combatant_ids: ["mara17"], natural_roll: 20, initiative_count: 25, tie_break_rolls: [] },
  { members: [scheduledMembers[1]], combatant_ids: ["target17"], natural_roll: 19, initiative_count: 19, tie_break_rolls: [] },
];
assert.deepEqual(
  window.IRON_PIT_BROWSER_INITIATIVE.firstRoundSchedule(naturalTwentyGroups).order,
  ["mara17", "target17", "mara17"],
  "the extra turn uses initiative -10 in the normal bucket rather than inheriting natural-20 priority",
);

const tiedExtraGroups = [
  { members: [scheduledMembers[0]], combatant_ids: ["mara17"], natural_roll: 14, initiative_count: 19, tie_break_rolls: [] },
  { members: [scheduledMembers[1]], combatant_ids: ["target17"], natural_roll: 9, initiative_count: 9, tie_break_rolls: [] },
];
assert.deepEqual(
  window.IRON_PIT_BROWSER_INITIATIVE.firstRoundSchedule(tiedExtraGroups).order,
  ["mara17", "target17", "mara17"],
  "a normal turn at the same initiative count resolves before the extra turn",
);

function state(template) {
  return {
    template, active_effect_ids: [], is_dead: false, is_unconscious: false,
    action_available: true, bonus_action_available: true, reaction_available: true,
    turn_terminated: false,
  };
}

const attacker = state({ name: "Visible attacker" });
const defender = state(rogue5);
let result = window.IRON_PIT_BROWSER_ROGUE_DEFENSES.applyUncannyDodge(
  attacker, defender, [{ source: "test", total: 21 }],
);
assert.equal(result.used, true);
assert.equal(result.components[0].total, 10);
assert.equal(defender.reaction_available, false);

const invisible = state({ name: "Invisible attacker" });
invisible.active_effect_ids.push("invisible");
const freshDefender = state(rogue5);
result = window.IRON_PIT_BROWSER_ROGUE_DEFENSES.applyUncannyDodge(
  invisible, freshDefender, [{ source: "test", total: 21 }],
);
assert.equal(result.used, false);
assert.equal(result.components[0].total, 21);
assert.equal(freshDefender.reaction_available, true);

const evader = state(rogue7);
assert.equal(window.IRON_PIT_BROWSER_ROGUE_DEFENSES.evasionDamage(evader, "dexterity", true, "half", 21), 0);
assert.equal(window.IRON_PIT_BROWSER_ROGUE_DEFENSES.evasionDamage(evader, "dexterity", false, "half", 21), 10);
assert.equal(window.IRON_PIT_BROWSER_ROGUE_DEFENSES.evasionDamage(evader, "constitution", true, "half", 21), 10);

window.IRON_PIT_BROWSER_FORMATION = {
  targetOrder: (_member, setup) => setup.monsters,
};
window.IRON_PIT_BROWSER_MODIFIERS = { effectiveSpeed: () => 30 };
window.IRON_PIT_BROWSER_OFFENSIVE_RANGES = { rangesForTarget: () => [{ family: "ranged", range: 80 }] };
window.IRON_PIT_BROWSER_STATE = { distance: (member, target) => Math.abs(member.position_ft - target.position_ft) };
load("browser-cunning-action.js");
const runner = { combatant_id: "mara", position_ft: 0, state: { ...state(rogue2), movement_remaining_ft: 30 } };
const farTarget = { combatant_id: "target", position_ft: 130, state: state({}) };
const setup = { heroes: [runner], monsters: [farTarget] };
assert.equal(window.IRON_PIT_BROWSER_CUNNING_ACTION.needsDash(runner, setup, "1:mara"), true);
const dash = window.IRON_PIT_BROWSER_CUNNING_ACTION.useDash(1, 1, runner, setup, "1:mara");
assert.equal(dash.feature_id, "cunning-action-dash");
assert.equal(runner.state.movement_remaining_ft, 60);
assert.equal(runner.state.bonus_action_available, false);

console.log("2014 Thief Rogue browser mechanics preserve shared Rogue mechanics through level 20 and edition isolation.");
