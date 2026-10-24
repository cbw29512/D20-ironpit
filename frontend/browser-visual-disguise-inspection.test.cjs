"use strict";
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();
const S = window.IRON_PIT_BROWSER_STATE;
const I = window.IRON_PIT_BROWSER_VISUAL_DISGUISE_INSPECTION;
const Attack = window.IRON_PIT_BROWSER_ATTACK;
const Saves = window.IRON_PIT_BROWSER_SAVES;
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
{
  const { observer, source } = makeFight();
  observer.state.active_effect_ids.push("blinded");
  assert.equal(I.recognizePhysicalInspection(observer.state, source.state, source.combatant_id), true);
  assert.deepEqual(observer.state.recognized_visual_disguise_source_ids, ["source"]);
  assert.equal(source.state.magical_visual_disguise_active, true);
  assert.equal(I.recognizePhysicalInspection(observer.state, source.state, source.combatant_id), false,
    "Recognition is observer-scoped and idempotent.");
}
{
  const { observer, source } = makeFight();
  source.state.template = {
    ...source.state.template,
    visualDisguiseAction: { ...source.state.template.visualDisguiseAction, physicalInspectionInconsistent: false },
  };
  assert.equal(I.recognizePhysicalInspection(observer.state, source.state, source.combatant_id), false);
  assert.deepEqual(observer.state.recognized_visual_disguise_source_ids, []);
}
{
  let fight = makeFight();
  let rolls = [15, 1];
  window.IRON_PIT_DICE = {
    roll: (sides) => ((rolls.shift() ?? 1) - 1) % sides + 1,
    rollMany: (n, sides) => Array.from({ length: n }, () => window.IRON_PIT_DICE.roll(sides)),
  };
  const plainAttack = { ...fight.observer.state.template.attacks[0] };
  const plain = Attack.resolveAttack(1, 1, fight.observer, fight.source, plainAttack, 5, { setup: fight.setup });
  assert.equal(plain.hit, true);
  assert.deepEqual(fight.observer.state.recognized_visual_disguise_source_ids, [],
    "Ordinary weapon contact is not physical inspection.");
  assert.equal(fight.source.state.magical_visual_disguise_active, true);

  fight = makeFight();
  rolls = [15, 1];
  window.IRON_PIT_DICE = {
    roll: (sides) => ((rolls.shift() ?? 1) - 1) % sides + 1,
    rollMany: (n, sides) => Array.from({ length: n }, () => window.IRON_PIT_DICE.roll(sides)),
  };
  const grappleAttack = {
    ...fight.observer.state.template.attacks[0],
    controlEffect: { grappleEscapeDc: 10 },
  };
  const grapple = Attack.resolveAttack(1, 1, fight.observer, fight.source, grappleAttack, 5, { setup: fight.setup });
  assert.equal(grapple.hit, true);
  assert.ok(grapple.applied_condition_ids.includes("grappled"));
  assert.deepEqual(fight.observer.state.recognized_visual_disguise_source_ids, ["source"]);
  assert.match(grapple.description, /recognizes .* visual disguise through physical inspection/);
  assert.equal(fight.source.state.magical_visual_disguise_active, true);
}
{
  const fight = makeFight();
  let rolls = [15, 1];
  window.IRON_PIT_DICE = {
    roll: (sides) => ((rolls.shift() ?? 1) - 1) % sides + 1,
    rollMany: (n, sides) => Array.from({ length: n }, () => window.IRON_PIT_DICE.roll(sides)),
  };
  const grappleAttack = {
    ...fight.source.state.template.attacks[0],
    controlEffect: { grappleEscapeDc: 10 },
  };
  const event = Attack.resolveAttack(1, 1, fight.source, fight.observer, grappleAttack, 5, { setup: fight.setup });
  assert.equal(event.hit, true);
  assert.ok(event.applied_condition_ids.includes("grappled"));
  assert.deepEqual(fight.observer.state.recognized_visual_disguise_source_ids, ["source"],
    "The creature held by a disguised grappler also detects the tactile inconsistency.");
  assert.equal(fight.source.state.magical_visual_disguise_active, true);
}
{
  const fight = makeFight();
  window.IRON_PIT_DICE = { roll: () => 1, rollMany: (n) => Array.from({ length: n }, () => 1) };
  const action = {
    id: "renamed-direct-grab", name: "Renamed Direct Grab", actionCost: "action",
    saveAbility: "strength", dc: 40, range: 5, maxTargets: 1,
    damageDiceCount: 0, damageDiceSize: 6, damageBonus: 0, successDamage: "none",
    grappleEscapeDc: 10, restrainsWhileGrappled: false, resourceCost: 1,
    magicalEffect: false, effectTags: [], automaticFailureCreatureTypes: [],
    requiredTargetCreatureTypes: [], prohibitedTargetSourceEffectIds: [], excludedTargetCreatureTypes: [],
  };
  const event = Saves.resolveAction(1, 1, fight.observer, fight.source, action, 5, { setup: fight.setup });
  assert.equal(event.save_succeeded, false);
  assert.ok(event.applied_condition_ids.includes("grappled"));
  assert.deepEqual(fight.observer.state.recognized_visual_disguise_source_ids, ["source"]);
  assert.match(event.description, /recognizes .* visual disguise through physical inspection/);
  assert.equal(fight.source.state.magical_visual_disguise_active, true);
}
assert.deepEqual(original, baseCard, "Source card must remain immutable.");
console.log("Source-neutral disguise Investigation uses printed ability, skill, DC, Action and real rolls.");
