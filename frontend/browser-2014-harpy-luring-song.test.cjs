"use strict";

const assert = require("node:assert/strict");
const { loadWebsite } = require("./browser-test-runtime.cjs");
loadWebsite();

const S = window.IRON_PIT_BROWSER_STATE;
const card = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-harpy"];
assert.ok(card, "the actual exported 2014 Harpy card must exist");
const original = JSON.stringify(card);
const action = card.saving_throw_actions.find((item) => item.id === "luring-song");
assert.ok(action, "the source-proven Luring Song must be exported");
assert.equal(action.actionCost, "action");
assert.equal(action.range, 300);
assert.equal(action.area.radius_ft, 300);
assert.deepEqual(action.requiredTargetCreatureTypes, ["humanoid", "giant"]);
assert.equal(action.requiresTargetHearing, true);
assert.equal(action.failedSaveTimedEffect.sourceMaintenanceActionCost, "bonus_action");
assert.equal(action.failedSaveTimedEffect.exclusiveSourceEffectGroupId, "audible-luring-song");
assert.equal(action.failedSaveTimedEffect.sourceEffectImmunityOnRepeatSaveSuccess, true);
assert.ok(!action.failedSaveTimedEffect.sourceEffectImmunityOnEnd);

const source = {
  combatant_id: "source", side: "monsters", position_ft: 0,
  state: S.buildState(structuredClone(card)),
};
const other = {
  combatant_id: "other-source", side: "monsters", position_ft: 0,
  state: S.buildState(structuredClone(card)),
};
const targetTemplate = structuredClone(window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"]);
targetTemplate.saving_throw_bonuses = { ...targetTemplate.saving_throw_bonuses, wisdom: 0 };
const target = {
  combatant_id: "target", side: "heroes", position_ft: 10,
  state: S.buildState(targetTemplate),
};
const giant = {
  combatant_id: "giant", side: "heroes", position_ft: 10,
  state: S.buildState({ ...structuredClone(targetTemplate), creature_type: "giant" }),
};
const beast = {
  combatant_id: "beast", side: "heroes", position_ft: 10,
  state: S.buildState({ ...structuredClone(targetTemplate), creature_type: "beast" }),
};
const deaf = {
  combatant_id: "deaf", side: "heroes", position_ft: 10,
  state: S.buildState(structuredClone(targetTemplate)),
};
deaf.state.active_effect_ids.push("deafened");
const setup = { heroes: [target, giant, beast, deaf], monsters: [source, other] };

assert.equal(window.IRON_PIT_BROWSER_SAVES.legalAction(action, target, 10, source.combatant_id, source), true);
assert.equal(window.IRON_PIT_BROWSER_SAVES.legalAction(action, giant, 10, source.combatant_id, source), true);
assert.equal(window.IRON_PIT_BROWSER_SAVES.legalAction(action, beast, 10, source.combatant_id, source), false);
assert.equal(window.IRON_PIT_BROWSER_SAVES.legalAction(action, deaf, 10, source.combatant_id, source), false);

window.IRON_PIT_DICE = {
  roll: (sides) => sides === 20 ? 1 : 1,
  rollMany: (count, sides) => Array.from({ length: count }, () => 1),
};
const event = window.IRON_PIT_BROWSER_SAVES.resolveAction(
  1, 1, source, target, action, 10,
);
assert.equal(event.save_succeeded, false);
assert.deepEqual(event.applied_condition_ids, ["charmed", "incapacitated"]);
assert.ok(target.state.active_effect_ids.includes("charmed"));
assert.ok(target.state.active_effect_ids.includes("incapacitated"));
assert.equal(window.IRON_PIT_BROWSER_SAVES.legalAction(
  action, target, 10, other.combatant_id, other,
), false, "an active target ignores competing songs");

source.state.turns_started = 1;
source.state.bonus_action_available = true;
const maintained = window.IRON_PIT_BROWSER_SOURCE_MAINTENANCE.resolve(
  2, 2, source, setup,
);
assert.equal(maintained.events[0].feature_id, "luring-song");
assert.equal(source.state.bonus_action_available, false);

window.IRON_PIT_DICE = { roll: () => 20, rollMany: () => [] };
const repeated = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(
  3, 2, target, "target_turn_end", setup,
);
assert.equal(repeated.events[0].save_succeeded, true);
assert.ok(!target.state.active_effect_ids.includes("charmed"));
assert.ok(!target.state.active_effect_ids.includes("incapacitated"));
assert.ok(target.state.timed_effects.some((effect) =>
  effect.effect_id.includes("luring-song:success-immunity:source")));
assert.equal(JSON.stringify(card), original, "fight state never mutates the printed card");
assert.ok(!S.buildState(card).active_effect_ids.includes("charmed"), "fresh fights reset");
console.log("2014 Harpy exported Luring Song lifecycle passed.");
