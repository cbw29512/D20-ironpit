"use strict";
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

const S = window.IRON_PIT_BROWSER_STATE;
const I = window.IRON_PIT_BROWSER_VISUAL_DISGUISE_INSPECTION;
const Attack = window.IRON_PIT_BROWSER_ATTACK;
const Saves = window.IRON_PIT_BROWSER_SAVES;
const base = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-commoner"];

function makeFight(physicalInspectionInconsistent = true) {
  try {
    const observer = {
      combatant_id: "observer", side: "heroes", position_ft: 0,
      state: S.buildState(structuredClone(base)),
    };
    const sourceCard = {
      ...structuredClone(base), name: "Renamed Visual Source",
      visualDisguiseAction: {
        id: "renamed-visual-mask", name: "Renamed Visual Mask",
        physicalInspectionInconsistent,
      },
    };
    const source = {
      combatant_id: "source", side: "monsters", position_ft: 5,
      state: S.buildState(sourceCard),
    };
    source.state.magical_visual_disguise_active = true;
    return { observer, source, setup: { heroes: [observer], monsters: [source] } };
  } catch (error) {
    console.error("Failed to build tactile disguise test fight", { error });
    throw error;
  }
}

function setDice(values) {
  try {
    const queue = [...values];
    window.IRON_PIT_DICE = {
      roll: (sides) => ((queue.shift() ?? 1) - 1) % sides + 1,
      rollMany: (count, sides) => Array.from(
        { length: count }, () => window.IRON_PIT_DICE.roll(sides),
      ),
    };
  } catch (error) {
    console.error("Failed to configure tactile disguise test dice", { error });
    throw error;
  }
}

{
  const { observer, source } = makeFight();
  observer.state.active_effect_ids.push("blinded");
  assert.equal(I.recognizePhysicalInspection(observer.state, source.state, "source"), true);
  assert.deepEqual(observer.state.recognized_visual_disguise_source_ids, ["source"]);
  assert.equal(source.state.magical_visual_disguise_active, true);
  assert.equal(I.recognizePhysicalInspection(observer.state, source.state, "source"), false);

  const other = makeFight(false);
  assert.equal(I.recognizePhysicalInspection(other.observer.state, other.source.state, "source"), false);
  assert.deepEqual(other.observer.state.recognized_visual_disguise_source_ids, []);
}

{
  let fight = makeFight();
  setDice([15, 1]);
  const plain = Attack.resolveAttack(
    1, 1, fight.observer, fight.source,
    { ...fight.observer.state.template.attacks[0] }, 5, { setup: fight.setup },
  );
  assert.equal(plain.hit, true);
  assert.deepEqual(fight.observer.state.recognized_visual_disguise_source_ids, []);

  fight = makeFight();
  setDice([15, 1]);
  const grapple = Attack.resolveAttack(
    1, 1, fight.observer, fight.source,
    { ...fight.observer.state.template.attacks[0], controlEffect: { grappleEscapeDc: 10 } },
    5, { setup: fight.setup },
  );
  assert.ok(grapple.applied_condition_ids.includes("grappled"));
  assert.deepEqual(fight.observer.state.recognized_visual_disguise_source_ids, ["source"]);
  assert.match(grapple.description, /recognizes .* visual disguise through physical inspection/);
  assert.equal(fight.source.state.magical_visual_disguise_active, true);
}

{
  const fight = makeFight();
  setDice([15, 1]);
  const event = Attack.resolveAttack(
    1, 1, fight.source, fight.observer,
    { ...fight.source.state.template.attacks[0], controlEffect: { grappleEscapeDc: 10 } },
    5, { setup: fight.setup },
  );
  assert.ok(event.applied_condition_ids.includes("grappled"));
  assert.deepEqual(fight.observer.state.recognized_visual_disguise_source_ids, ["source"]);
  assert.equal(fight.source.state.magical_visual_disguise_active, true);
}

{
  const fight = makeFight();
  setDice([1]);
  const action = {
    id: "renamed-direct-grab", name: "Renamed Direct Grab", actionCost: "action",
    saveAbility: "strength", dc: 40, range: 5, maxTargets: 1,
    damageDiceCount: 0, damageDiceSize: 6, damageBonus: 0, successDamage: "none",
    grappleEscapeDc: 10, restrainsWhileGrappled: false, resourceCost: 1,
    magicalEffect: false, effectTags: [], automaticFailureCreatureTypes: [],
    requiredTargetCreatureTypes: [], prohibitedTargetSourceEffectIds: [], excludedTargetCreatureTypes: [],
  };
  const event = Saves.resolveAction(
    1, 1, fight.observer, fight.source, action, 5, { setup: fight.setup },
  );
  assert.equal(event.save_succeeded, false);
  assert.ok(event.applied_condition_ids.includes("grappled"));
  assert.deepEqual(fight.observer.state.recognized_visual_disguise_source_ids, ["source"]);
  assert.match(event.description, /recognizes .* visual disguise through physical inspection/);
  assert.equal(fight.source.state.magical_visual_disguise_active, true);
}

console.log("Universal tactile visual-disguise inspection regressions passed.");
