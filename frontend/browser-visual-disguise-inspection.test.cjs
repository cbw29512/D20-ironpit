"use strict";
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();
const S = window.IRON_PIT_BROWSER_STATE;
const I = window.IRON_PIT_BROWSER_VISUAL_DISGUISE_INSPECTION;
assert.ok(I?.inspect, "Shared visual inspection module must be loaded by the site.");
const original = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-commoner"];
assert.ok(original, "Real 2014 card must exist.");
const baseCard = structuredClone(original);
const declared = {
  id: "any-visual-mask", name: "Renamed Illusion",
  activationCost: "action", dismissalCost: "bonus_action",
  concealsTrueForm: true, magicalIllusion: true, endsIfOwnerDead: true,
  physicalInspectionInconsistent: true, inspectionCost: "action",
  inspectionAbility: "intelligence", inspectionSkill: "investigation", inspectionDc: 16,
  investigationRevealsTrueForm: false, openingEligible: true,
  openingPriority: 20, dismissOnFirstTurn: true,
};
function makeFight({ roll=12, modifier=4, dc=16, cost="action", sourceKind="monster" } = {}) {
  const card = { ...structuredClone(original), kind: "character",
    ability_scores: { strength: 10, dexterity: 10, constitution: 10, intelligence: 10, wisdom: 10, charisma: 10 },
    skill_bonuses: { investigation: modifier } };
  const sourceCard = { ...structuredClone(original), kind: sourceKind, name: "Generic Mask",
    visualDisguiseAction: { ...declared, inspectionDc: dc, inspectionCost: cost } };
  const observer = { combatant_id: "observer", side: "heroes", position_ft: 0, state: S.buildState(card) };
  const source = { combatant_id: "source", side: "monsters", position_ft: 10, state: S.buildState(sourceCard) };
  source.state.magical_visual_disguise_active = true;
  window.IRON_PIT_DICE = { roll: sides => { assert.equal(sides, 20); return roll; },
    rollMany: (n, sides) => Array.from({ length: n }, () => roll) };
  return { observer, source, setup: { heroes: [observer], monsters: [source] } };
}
{
  const { observer, source, setup } = makeFight();
  const event = I.inspect(1, 1, observer, source, setup);
  assert.equal(event.check_dc, 16);
  assert.equal(event.ability_check_roll.total, 16);
  assert.equal(event.check_succeeded, true);
  assert.deepEqual(observer.state.recognized_visual_disguise_source_ids, ["source"]);
  assert.equal(observer.state.action_available, false);
  assert.equal(observer.state.bonus_action_available, true);
  assert.equal(source.state.magical_visual_disguise_active, true);
  assert.equal(S.buildState(observer.state.template).recognized_visual_disguise_source_ids.length, 0);
}
{
  const { observer, source, setup } = makeFight({ roll: 11 });
  const event = I.inspect(1, 1, observer, source, setup);
  assert.equal(event.check_succeeded, false);
  assert.equal(observer.state.action_available, false);
  assert.deepEqual(observer.state.recognized_visual_disguise_source_ids, []);
  assert.throws(() => I.inspect(2, 1, observer, source, setup), /unavailable/);
}
{
  const { observer, source, setup } = makeFight({ dc: 18, sourceKind: "character" });
  const event = I.inspect(1, 1, observer, source, setup);
  assert.equal(event.check_dc, 18);
  assert.equal(event.check_succeeded, false);
}
{
  const { observer, source, setup } = makeFight({ roll: 1, modifier: 16 });
  assert.equal(I.inspect(1, 1, observer, source, setup).check_succeeded, true,
    "Natural 1 is not automatic failure for a skill check.");
}
{
  const { observer, source, setup } = makeFight({ roll: 20, modifier: -10 });
  assert.equal(I.inspect(1, 1, observer, source, setup).check_succeeded, false,
    "Natural 20 is not automatic success for a skill check.");
}
{
  const { observer, source, setup } = makeFight({ roll: 15, modifier: 4, dc: 19, cost: "bonus_action" });
  assert.equal(I.inspect(1, 1, observer, source, setup).check_succeeded, true);
  assert.equal(observer.state.action_available, true);
  assert.equal(observer.state.bonus_action_available, false);
}
{
  const { observer, source, setup } = makeFight();
  source.state.magical_visual_disguise_active = false;
  assert.throws(() => I.inspect(1, 1, observer, source, setup), /no active visual disguise/);
  source.state.magical_visual_disguise_active = true;
  observer.state.active_effect_ids.push("blinded");
  assert.throws(() => I.inspect(1, 1, observer, source, setup), /requires sight/);
}
assert.deepEqual(original, baseCard, "Source card must remain immutable.");
console.log("Source-neutral disguise Investigation uses printed ability, skill, DC, Action and real rolls.");
