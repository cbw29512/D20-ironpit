"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = name => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name }
);
let success = false, zeroHpCalls = 0;
window.IRON_PIT_BROWSER_SAVING_THROWS = {
  resolveSavingThrow: () => ({ roll: { notation: "1d20", total: success ? 20 : 1 }, succeeded: success }),
};
window.IRON_PIT_BROWSER_STATE = { distance: () => 5, sizeAtMost: () => true };
window.IRON_PIT_BROWSER_CONDITION_RULES = {
  has: (state, name) => state.active_effect_ids.includes(name)
    && !(state.suppressed_effect_ids || []).includes(name),
  canSee: state => !state.active_effect_ids.includes("blinded"),
};
window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS = { saveAdvantageSourceNames: () => [] };
window.IRON_PIT_BROWSER_ZERO_HP = { reduceToZero: state => {
  zeroHpCalls++; state.current_hp = 0; state.is_unconscious = true; return "unconscious";
} };
window.IRON_PIT_BROWSER_ROGUE_DEFENSES = { evasionDamage: (_s, _a, _ok, _mode, n) => n };
window.IRON_PIT_BROWSER_ATTACK = { applyDamage: () => { throw new Error("Must not apply damage"); } };
load("browser-save-immunity.js");
load("browser-save-action-support.js");
load("browser-save-action-attempt.js");
load("browser-save-damage.js");
load("browser-save-damage-legacy.js");
load("browser-save-damage-apply.js");
load("browser-save-action-effects.js");
load("browser-save-event.js");
load("browser-saves.js");
const S = window.IRON_PIT_BROWSER_SAVES;
const actor = { combatant_id: "source", side: "monsters", state: {
  template: { name: "Any Source", creature_type: "fey" },
  current_hp: 40, active_effect_ids: [], resources: {}, action_available: true,
} };
const target = { combatant_id: "target", side: "heroes", state: {
  template: { name: "Any Hero", kind: "character", creature_type: "humanoid" },
  current_hp: 40, active_effect_ids: [], is_alive: true, is_dead: false,
  death_save_successes: 0, death_save_failures: 0,
} };
const action = { id: "renamed-glare", name: "Renamed Conditioned Save",
  range: 30, dc: 11, saveAbility: "wisdom", requiredTargetCondition: "frightened",
  requiresTargetSight: true, requiresTargetToSeeSource: true,
  failureSetsZeroHp: true, magicalEffect: true };
assert.equal(S.legalAction(action, target, 5, actor.combatant_id, actor), false);
target.state.active_effect_ids.push("frightened");
assert.equal(S.legalAction(action, target, 5, actor.combatant_id, actor), true);
target.state.suppressed_effect_ids = ["frightened"];
assert.equal(S.legalAction(action, target, 5, actor.combatant_id, actor), false);
target.state.suppressed_effect_ids = [];
actor.state.active_effect_ids.push("blinded");
assert.equal(S.legalAction(action, target, 5, actor.combatant_id, actor), false);
actor.state.active_effect_ids.pop();
target.state.active_effect_ids.push("blinded");
assert.equal(S.legalAction(action, target, 5, actor.combatant_id, actor), false);
target.state.active_effect_ids.pop();
assert.equal(S.legalAction(action, target, 31, actor.combatant_id, actor), false);
assert.equal(S.legalAction({ ...action, name: "Another Ability" }, target, 5, actor.combatant_id, actor), true);
success = true;
let event = S.resolveAction(1, 1, actor, target, action, 5, { spendAction: false });
assert.equal(event.save_succeeded, true);
assert.equal(target.state.current_hp, 40);
success = false;
event = S.resolveAction(2, 1, actor, target, action, 5, { spendAction: false });
assert.equal(event.save_succeeded, false);
assert.equal(target.state.current_hp, 0);
assert.equal(zeroHpCalls, 1);
assert.match(event.description, /Renamed Conditioned Save/);
// A target must be grappled by THIS actor, not merely Grappled.
const heldSave = { ...action, name: "Renamed Source Hold", requiredTargetCondition: null,
  requiresTargetSight: false, requiresTargetToSeeSource: false, failureSetsZeroHp: false,
  requiresTargetGrappledBySource: true, maxTargets: 2, targetScope: "all-other-creatures" };
target.state.grapple_sources = [{ source_id: "different-source" }];
target.state.active_effect_ids.push("grappled");
assert.equal(S.legalAction(heldSave, target, 5, actor.combatant_id, actor), false);
assert.equal(S.legalAction(heldSave, target, 5, "different-source", actor), false);
target.state.grapple_sources = [{ source_id: actor.combatant_id }];
assert.equal(S.legalAction(heldSave, target, 5, actor.combatant_id, actor), true);
const other = { ...target, combatant_id: "other", state: { ...target.state,
  grapple_sources: [{ source_id: "different-source" }] } };
const ally = { ...target, combatant_id: "ally", side: actor.side, state: { ...target.state,
  grapple_sources: [{ source_id: actor.combatant_id }] } };
window.IRON_PIT_ACTION_ECONOMY = { available: () => true };
window.IRON_PIT_BROWSER_RESOURCES = { available: () => true };
window.IRON_PIT_BROWSER_FORMATION = { targetOrder: () => [target, other], saveDistance: () => 5 };
actor.state.template.saving_throw_actions = [heldSave];
load("browser-multi-save-provider.js");
const selection = window.IRON_PIT_BROWSER_MULTI_SAVE_PROVIDER.choose(actor,
  { heroes: [target, other], monsters: [actor, ally] });
assert.deepEqual(selection.targets.map((item) => item.combatant_id), ["target", "ally"]);
target.state.grapple_sources = [];
assert.equal(S.legalAction(heldSave, target, 5, actor.combatant_id, actor), false);
console.log("Condition-gated saves and source-owned grapple targeting passed.");
