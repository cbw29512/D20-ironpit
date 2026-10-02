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

window.IRON_PIT_BROWSER_CONDITION_RULES = { incapacitated: () => false };
window.IRON_PIT_BROWSER_TIMED = {
  suppressesAction: () => false,
  suppressesBonusAction: () => false,
  suppressesReactions: () => false,
};
window.IRON_PIT_DICE = { roll: () => 10 };

load("browser-heroes.js");
load("browser-action-economy.js");
load("browser-attack-damage-reduction.js");

const l12 = structuredClone(window.IRON_PIT_BROWSER_HEROES["kael-stillwater-l12"]);
const l13 = structuredClone(window.IRON_PIT_BROWSER_HEROES["kael-stillwater-l13"]);

assert.ok(l12);
assert.ok(l13);
assert.deepEqual(
  l12.attackDamageReductionReaction.requiredDamageTypes,
  ["bludgeoning", "piercing", "slashing"],
);
assert.deepEqual(l13.attackDamageReductionReaction.requiredDamageTypes, []);
assert.equal(l13.resources["focus-points"], 13);
assert.equal(l13.initiative_bonus, 10);
assert.equal(l13.attacks[0].attackBonus, 10);
assert.equal(l13.attackDamageReductionReaction.zeroDamageRedirect.saveDc, 14);
assert.equal(l13.attackDamageReductionReaction.zeroDamageRedirect.damageDiceSize, 10);

const state12 = {
  template: l12,
  current_hp: l12.max_hp,
  reaction_available: true,
  is_dead: false,
  is_unconscious: false,
  turn_terminated: false,
  active_effect_ids: [],
};
const state13 = {
  template: l13,
  current_hp: l13.max_hp,
  reaction_available: true,
  is_dead: false,
  is_unconscious: false,
  turn_terminated: false,
  active_effect_ids: [],
};
const attack = { kind: "melee" };
const fire = [{
  source: "test-fire",
  notation: "8",
  rolls: [],
  modifier: 8,
  damage_type: "fire",
  total: 8,
}];

assert.equal(window.IRON_PIT_BROWSER_ATTACK_DAMAGE_REDUCTION.eligible(state12, attack, fire), false);
assert.equal(window.IRON_PIT_BROWSER_ATTACK_DAMAGE_REDUCTION.eligible(state13, attack, fire), true);

const reduced = window.IRON_PIT_BROWSER_ATTACK_DAMAGE_REDUCTION.apply(state13, attack, fire);
assert.equal(reduced.used, true);
assert.equal(reduced.zeroedAttack, true);
assert.equal(reduced.components[0].total, 0);

console.log("Browser 2024 Monk level 13 regressions passed.");
