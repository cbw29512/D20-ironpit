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
window.IRON_PIT_BROWSER_GRAPPLE = { speedIsZero: () => false };
window.IRON_PIT_BROWSER_TIMED = {
  suppressesAction: () => false,
  suppressesBonusAction: () => false,
  suppressesReactions: () => false,
};
window.IRON_PIT_BROWSER_MODIFIERS = { effectiveSpeed: (state) => state.template.speed_ft };
window.IRON_PIT_BROWSER_RESOURCES = {
  available: (state, id, cost = 1) => !id || (state.resources[id] || 0) >= cost,
  spend: (state, id, cost = 1) => {
    if (!id) return null;
    state.resources[id] -= cost;
    return state.resources[id];
  },
};
window.IRON_PIT_BROWSER_FORMATION = { targetOrder: (_member, setup) => setup.monsters };
window.IRON_PIT_BROWSER_OFFENSIVE_RANGES = {
  rangesForTarget: () => [{ family: "attack", range: 5 }],
};
window.IRON_PIT_BROWSER_STATE = {
  distance: (member, target) => Math.abs(member.position_ft - target.position_ft),
};

load("browser-action-economy.js");
load("browser-ability-hooks.js");
load("browser-dodge.js");
load("browser-tactical-actions.js");

function monk() {
  return {
    combatant_id: "monk",
    side: "heroes",
    position_ft: 0,
    state: {
      template: {
        name: "Kael Stillwater",
        ruleset: "2024",
        speed_ft: 40,
        bonusTacticalActionGrants: [
          {
            id: "step-of-the-wind-dash",
            name: "Step of the Wind",
            effects: ["dash"],
            resourceId: null,
            resourceCost: 1,
            priority: 40,
            usePolicy: "enable-offense",
            jumpDistanceMultiplier: 1,
          },
          {
            id: "patient-defense-focus",
            name: "Patient Defense",
            effects: ["disengage", "dodge"],
            resourceId: "focus",
            resourceCost: 1,
            priority: 90,
            usePolicy: "defensive-fallback",
            jumpDistanceMultiplier: 1,
          },
        ],
      },
      resources: { focus: 2 },
      action_available: true,
      bonus_action_available: true,
      reaction_available: true,
      movement_remaining_ft: 40,
      active_effect_ids: [],
      disengaged_this_turn: false,
      turn_terminated: false,
      is_dead: false,
      is_unconscious: false,
    },
  };
}

{
  const actor = monk();
  const target = { combatant_id: "target", side: "monsters", position_ft: 70, state: { current_hp: 10 } };
  const setup = { heroes: [actor], monsters: [target] };
  const grant = window.IRON_PIT_BROWSER_TACTICAL_ACTIONS.chooseOffensiveDashGrant(
    actor, setup, "1:monk",
  );
  assert.equal(grant.id, "step-of-the-wind-dash");
  const event = window.IRON_PIT_BROWSER_TACTICAL_ACTIONS.useOffensiveDash(
    1, 1, actor, setup, "1:monk",
  );
  assert.equal(event.feature_id, "step-of-the-wind-dash");
  assert.equal(event.movement_ft, 40);
  assert.equal(actor.state.movement_remaining_ft, 80);
  assert.equal(actor.state.resources.focus, 2);
  assert.equal(actor.state.bonus_action_available, false);
}

{
  const actor = monk();
  const grant = actor.state.template.bonusTacticalActionGrants[1];
  const event = window.IRON_PIT_BROWSER_TACTICAL_ACTIONS.resolve(1, 1, actor, grant);
  assert.equal(event.feature_id, "patient-defense-focus");
  assert.equal(actor.state.resources.focus, 1);
  assert.equal(actor.state.disengaged_this_turn, true);
  assert.ok(actor.state.active_effect_ids.includes("dodge"));
  assert.equal(actor.state.bonus_action_available, false);
}

{
  const actor = monk();
  window.IRON_PIT_BROWSER_TACTICAL_ACTIONS.installAbilityHooks();
  const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
  const result = hooks.runPhase(hooks.PHASES.BONUS_ACTION_WINDOW, {
    sequence: 1,
    round: 1,
    member: actor,
    setup: { heroes: [actor], monsters: [] },
    turnKey: "1:monk",
    bonusActionCheckpoint: "postAction",
    events: [],
  });
  assert.equal(result.claimed, true);
  assert.equal(result.events[0].feature_id, "patient-defense-focus");
  assert.equal(actor.state.resources.focus, 1);
  assert.ok(actor.state.active_effect_ids.includes("dodge"));
}

{
  const rogue = monk();
  rogue.combatant_id = "rogue";
  rogue.state.template.ruleset = "2014";
  rogue.state.template.cunning_action = true;
  rogue.state.template.bonusTacticalActionGrants = [];
  const grants = window.IRON_PIT_BROWSER_TACTICAL_ACTIONS.grants(rogue);
  assert.equal(grants.length, 1);
  assert.equal(grants[0].id, "cunning-action-dash");
  assert.equal(grants[0].usePolicy, "enable-offense");
}

console.log("Browser universal tactical Bonus Action regressions passed.");
