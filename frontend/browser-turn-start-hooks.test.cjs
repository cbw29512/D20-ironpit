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

window.IRON_PIT_DICE = {
  roll: (sides) => {
    assert.equal(sides, 6);
    return 5;
  },
};

load("browser-ability-hooks.js");
load("browser-recharge.js");

window.IRON_PIT_BROWSER_STATE = {
  distance: (a, b) => Math.abs((a.position_ft || 0) - (b.position_ft || 0)),
};
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
load("browser-condition-rules.js");
load("browser-timed-conditions.js");
window.IRON_PIT_BROWSER_SAVES = {
  resolveSavingThrow: (_state, ability, dc) => ({
    roll: { notation: "1d20+2", rolls: [1], modifier: 2, total: 3, selected_roll: 1 },
    succeeded: false,
    ability,
    dc,
  }),
};
load("browser-timed-emanations.js");

const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
const registered = hooks.abilitiesFor(hooks.PHASES.TURN_START);
assert.equal(registered.some((ability) => ability.id === "recharge"), true);

const member = {
  combatant_id: "recharge-monster",
  state: {
    resources: { breath: 0 },
    template: {
      name: "Recharge Monster",
      ruleset: "2024",
      recharge_rules: [{ resourceId: "breath", minimumRoll: 5, dieSize: 6 }],
    },
  },
};
const result = hooks.runPhase(hooks.PHASES.TURN_START, {
  sequence: 10,
  round: 2,
  member,
  setup: { heroes: [], monsters: [member] },
  turnKey: "2:recharge-monster",
  events: [],
});

assert.equal(result.events.length, 1);
assert.equal(result.events[0].recharge_succeeded, true);
assert.equal(result.sequence, 11);
assert.equal(result.claimed, false);
assert.equal(member.state.resources.breath, 1);

const auraSource = {
  combatant_id: "aura-source", side: "heroes", position_ft: 0,
  state: {
    timed_effects: [{
      effect_id: "draconic-presence-fear",
      source_id: "aura-source",
      source_effect_id: "draconic-presence-fear",
    }],
    template: {
      name: "Aura Source",
      timed_self_buff_actions: [{
        id: "draconic-presence-fear",
        name: "Draconic Presence: Fear",
        durationRounds: 10,
        expiryTiming: "source_turn_start",
        animation: "draconic-presence",
        hostileStartTurnConditionAura: {
          trigger: "enemy_turn_start",
          radius_ft: 60,
          save_ability: "wisdom",
          save_dc: 19,
          condition_id: "frightened",
          success_immunity: true,
          source_is_magical: true,
        },
      }],
    },
  },
};
const auraTarget = {
  combatant_id: "aura-target", side: "monsters", position_ft: 30,
  state: {
    is_alive: true, is_dead: false, active_effect_ids: [], timed_effects: [],
    template: { name: "Aura Target", saving_throw_bonuses: { wisdom: 2 }, condition_immunities: [] },
  },
};
const auraResult = window.IRON_PIT_BROWSER_TIMED_EMANATIONS.resolveStartOfTurn(
  result.sequence,
  2,
  auraTarget,
  { heroes: [auraSource], monsters: [auraTarget] },
);
assert.equal(auraResult.events.length, 1);
assert.equal(auraResult.events[0].feature_id, "draconic-presence-fear");
assert.equal(auraResult.events[0].save_succeeded, false);
assert.ok(auraTarget.state.active_effect_ids.includes("frightened"));


const passiveSource = {
  combatant_id: "hezrou", side: "monsters", position_ft: 0,
  state: {
    is_alive: true, is_dead: false, timed_effects: [],
    template: {
      name: "Hezrou",
      timed_self_buff_actions: [{
        id: "hezrou-stench", name: "Stench", activationTiming: "passive",
        durationRounds: 1, expiryTiming: "target_turn_start", animation: "stench",
        hostileStartTurnConditionAura: {
          trigger: "enemy_turn_start",
          radius_ft: 10,
          save_ability: "constitution",
          save_dc: 14,
          condition_id: "poisoned",
          success_immunity: true,
          source_is_magical: false,
        },
      }],
    },
  },
};
const passiveTarget = {
  combatant_id: "stench-target", side: "heroes", position_ft: 5,
  state: {
    is_alive: true, is_dead: false, active_effect_ids: [], timed_effects: [],
    template: {
      name: "Stench Target",
      saving_throw_bonuses: { constitution: 0 },
      condition_immunities: [],
    },
  },
};
const passiveActionBefore = JSON.stringify(passiveSource.state.template.timed_self_buff_actions[0]);
const passiveResult = window.IRON_PIT_BROWSER_TIMED_EMANATIONS.resolveStartOfTurn(
  auraResult.sequence,
  2,
  passiveTarget,
  { heroes: [passiveTarget], monsters: [passiveSource] },
);
assert.equal(passiveResult.events.length, 1);
assert.equal(passiveResult.events[0].feature_id, "hezrou-stench");
assert.equal(passiveResult.events[0].save_succeeded, false);
assert.ok(passiveTarget.state.active_effect_ids.includes("poisoned"));
assert.equal(passiveTarget.state.timed_effects[0].expiry_timing, "target_turn_start");
assert.equal(passiveTarget.state.timed_effects[0].expires_round, 3);
assert.equal(JSON.stringify(passiveSource.state.template.timed_self_buff_actions[0]), passiveActionBefore);

passiveSource.state.is_alive = false;
passiveSource.state.is_dead = true;
const deadSourceTarget = {
  ...passiveTarget,
  combatant_id: "dead-source-target",
  state: {
    ...passiveTarget.state,
    active_effect_ids: [],
    timed_effects: [],
  },
};
const deadSourceResult = window.IRON_PIT_BROWSER_TIMED_EMANATIONS.resolveStartOfTurn(
  passiveResult.sequence,
  3,
  deadSourceTarget,
  { heroes: [deadSourceTarget], monsters: [passiveSource] },
);
assert.deepEqual(deadSourceResult.events, []);

const turnSource = fs.readFileSync(path.join(__dirname, "browser-turn.js"), "utf8");
assert.equal(turnSource.includes("resolveStartOfTurn"), false);
assert.match(turnSource, /PHASES\.TURN_START/);

console.log("Browser turnStart Recharge hook migration passed.");
