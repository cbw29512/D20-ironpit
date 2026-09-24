"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(`frontend/${name}`, "utf8"), { filename: name });

window.IRON_PIT_BROWSER_GRAPPLE = { speedIsZero: () => false };
window.IRON_PIT_BROWSER_MODIFIERS = { effectiveSpeed: (state) => state.template.speed_ft };
for (const file of [
  "browser-condition-immunity.js", "browser-timed-conditions.js", "browser-state.js",
  "browser-survival-wards.js", "browser-zero-hp.js", "browser-precombat-spells.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const Z = window.IRON_PIT_BROWSER_ZERO_HP;
const P = window.IRON_PIT_BROWSER_PRECOMBAT_SPELLS;
const template = {
  id: "survival-test", name: "Survival Test", kind: "character", ruleset: "2014",
  max_hp: 20, speed_ft: 30, size: "medium", traits: ["relentless-endurance"],
  resources: { "spell-slot-4": 1, "relentless-endurance": 1 },
};
const spell = {
  id: "test-survival-ward", name: "Test Survival Ward", level: 4, actionCost: "action",
  range: 5, durationMinutes: 480, targetPolicy: "friendly", targetCount: 1,
  temporaryHp: 0, maxHpIncrease: 0, currentHpIncrease: 0,
  damageResistances: [], modifierEffects: [], concentration: false,
  survivalWard: { replacementHp: 1, preventsNondamageInstantDeath: true },
};

const member = { combatant_id: "target", side: "heroes", position_ft: 0, state: S.buildState(structuredClone(template)) };
P.resolve(1, member, [member], spell, 4);
assert.equal(Z.applyDamage(member.state, 40), "survival_ward");
assert.equal(member.state.current_hp, 1);
assert.equal(member.state.resources["relentless-endurance"], 1);
assert.match(member.state.pending_survival_save_logs.join(" "), /Test Survival Ward/);
assert.equal(Z.applyInstantDeath(member.state), "dead");

const second = { combatant_id: "second", side: "heroes", position_ft: 0, state: S.buildState(structuredClone(template)) };
P.resolve(1, second, [second], spell, 4);
assert.equal(Z.applyInstantDeath(second.state), "survival_ward");
assert.equal(second.state.current_hp, 1);
assert.equal(second.state.is_dead, false);

console.log("Universal browser survival-ward regressions passed.");
