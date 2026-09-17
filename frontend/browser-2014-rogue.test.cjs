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
load("browser-rogue-defenses.js");

const heroes = Object.values(window.IRON_PIT_BROWSER_HEROES);
const rogue2 = heroes.find((hero) => hero.id === "mara-quickstep-2014-l2");
const rogue5 = heroes.find((hero) => hero.id === "mara-quickstep-2014-l5");
const rogue7 = heroes.find((hero) => hero.id === "mara-quickstep-2014-l7");
const rogue10 = heroes.find((hero) => hero.id === "mara-quickstep-2014-l10");
assert.ok(rogue2 && rogue5 && rogue7 && rogue10);
assert.equal(rogue2.ruleset, "2014");
assert.equal(rogue2.cunning_action, true);
assert.equal(rogue5.uncanny_dodge, true);
assert.equal(rogue7.evasion, true);
assert.equal(rogue10.sneak_attack_d6, 5);
assert.deepEqual(rogue10.weapon_masteries, []);
assert.ok(rogue10.attacks.every((attack) => attack.masteryProperty == null));

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

console.log("2014 Thief Rogue browser mechanics preserve Cunning Action, Uncanny Dodge, Evasion, and edition isolation.");
