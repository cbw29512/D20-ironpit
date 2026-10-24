"use strict";

const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

const S = window.IRON_PIT_BROWSER_STATE;
const B = window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS;
const base = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-commoner"];

function fight(endsIfOwnerDead) {
  const action = {
    id: "unrelated-visual-mask",
    name: "Unrelated Visual Mask",
    activationCost: "action",
    dismissalCost: "bonus_action",
    concealsTrueForm: true,
    magicalIllusion: true,
    endsIfOwnerDead,
    physicalInspectionInconsistent: true,
    inspectionCost: "action",
    inspectionAbility: "intelligence",
    inspectionSkill: "investigation",
    inspectionDc: 17,
    investigationRevealsTrueForm: false,
    openingPriority: 20,
    openingEligible: true,
    dismissOnFirstTurn: true,
  };
  const template = {
    ...structuredClone(base),
    id: "renamed-visual-source",
    name: "Renamed Source",
    visualDisguiseAction: action,
  };
  const source = {
    combatant_id: "source",
    side: "monsters",
    state: S.buildState(template),
  };
  const target = {
    combatant_id: "target",
    side: "heroes",
    state: S.buildState(structuredClone(base)),
  };
  source.state.magical_visual_disguise_active = true;
  return { source, setup: { heroes: [target], monsters: [source] }, action };
}

{
  const { source, setup, action } = fight(true);
  source.state.current_hp = 0;
  source.state.is_alive = false;
  source.state.is_dead = true;

  B.cleanupDisabledSources(setup);

  assert.equal(source.state.magical_visual_disguise_active, false);
  assert.deepEqual(source.state.template.visualDisguiseAction, action);
  assert.equal(
    S.buildState(source.state.template).magical_visual_disguise_active,
    false,
  );
}

{
  const { source, setup, action } = fight(false);
  source.state.current_hp = 0;
  source.state.is_alive = false;
  source.state.is_dead = true;

  B.cleanupDisabledSources(setup);

  assert.equal(source.state.magical_visual_disguise_active, true);
  assert.deepEqual(source.state.template.visualDisguiseAction, action);
}

console.log("Visual disguise owner-death lifecycle parity passed.");
