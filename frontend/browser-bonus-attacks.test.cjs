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
window.IRON_PIT_BROWSER_RESOURCES = {
  available: (state, resourceId, cost = 1) => !resourceId || (state.resources[resourceId] || 0) >= cost,
  spend: (state, resourceId, cost = 1) => {
    if (resourceId) state.resources[resourceId] -= cost;
  },
};
window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH = null;
window.IRON_PIT_BROWSER_STATE = {
  nearestTarget: (_member, setup) => setup.monsters[0] || null,
  distance: () => 5,
  packTactics: () => false,
};
window.IRON_PIT_BROWSER_ATTACK = {
  resolveAttack(sequence, round, actor, target, attack, _distance, options) {
    return {
      sequence,
      round_number: round,
      event_type: "attack",
      actor_id: actor.combatant_id,
      target_id: target.combatant_id,
      weapon_id: attack.weaponId,
      feature_id: options.featureId,
      description: "Bonus Action attack test.",
    };
  },
};

load("browser-action-economy.js");
load("browser-ability-hooks.js");
load("browser-bonus-attacks.js");

const attack = {
  id: "kael-2024-unarmed", weaponId: "unarmed-strike",
  kind: "melee", reach: 5, bonus: 5, diceCount: 1, diceSize: 6, damageBonus: 3,
};
const actor = {
  combatant_id: "monk",
  side: "heroes",
  position_ft: 0,
  state: {
    template: {
      name: "Kael Stillwater",
      ruleset: "2024",
      attacks: [attack],
      bonusAttackGrants: [{
        id: "martial-arts", name: "Martial Arts",
        attackIds: ["kael-2024-unarmed"], attackCount: 1,
        resourceId: null, resourceCost: 1, priority: 90,
      }],
    },
    resources: {},
    action_available: true,
    bonus_action_available: true,
    reaction_available: true,
    turn_terminated: false,
    is_dead: false,
    is_unconscious: false,
  },
};
const target = {
  combatant_id: "target",
  side: "monsters",
  position_ft: 5,
  state: { template: { ruleset: "2024" }, current_hp: 10, is_alive: true, is_dead: false },
};
const setup = { heroes: [actor], monsters: [target] };

{
  const result = window.IRON_PIT_BROWSER_BONUS_ATTACKS.resolve(
    1, 1, actor, setup, "1:monk",
  );
  assert.equal(result.sequence, 2);
  assert.deepEqual(result.events.map((event) => event.feature_id), ["martial-arts"]);
  assert.equal(actor.state.bonus_action_available, false);
  assert.equal(actor.state.action_available, true,
    "2024 Martial Arts must not spend or require the Attack action");
}

{
  actor.state.bonus_action_available = true;
  window.IRON_PIT_BROWSER_BONUS_ATTACKS.installAbilityHooks();
  const H = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
  const result = H.runPhase(H.PHASES.BONUS_ACTION_WINDOW, {
    sequence: 1,
    round: 1,
    member: actor,
    setup,
    turnKey: "1:monk",
    bonusActionCheckpoint: "postAction",
    turnEvents: [],
    events: [],
  });
  assert.equal(result.claimed, true);
  assert.deepEqual(result.events.map((event) => event.feature_id), ["martial-arts"]);
}

{
  const legacy = structuredClone(actor);
  legacy.combatant_id = "legacy-monk";
  legacy.state.template.ruleset = "2014";
  legacy.state.template.bonusAttackGrants = [];
  legacy.state.bonus_action_available = true;
  const result = window.IRON_PIT_BROWSER_BONUS_ATTACKS.resolve(
    1, 1, legacy, setup, "1:legacy-monk",
  );
  assert.deepEqual(result.events, []);
  assert.equal(result.sequence, 1);
  assert.equal(legacy.state.bonus_action_available, true);
}

console.log("Browser universal Bonus Action attack regressions passed.");
