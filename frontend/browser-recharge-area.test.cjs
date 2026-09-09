"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

const saveRolls = [1, 20];
let damageRollCalls = 0;
window.IRON_PIT_BROWSER_ROLLS = {
  modeFromSources: () => "normal",
  d20: (bonus) => {
    const natural = saveRolls.shift();
    return { natural, total: natural + bonus, mode: "normal", rolls: [natural], modifier: bonus };
  },
};
window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage: (_state, amount) => amount,
  applyDamage: (state, amount) => { state.current_hp -= amount; return null; },
};
window.IRON_PIT_BROWSER_GRAPPLE = { apply: () => [] };
window.IRON_PIT_BROWSER_STATE = {
  distance: () => 5,
  sizeAtMost: () => true,
  packTactics: () => false,
};
window.IRON_PIT_BROWSER_CONDITION_RULES = { autoFailStrDex: () => false };
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => Boolean(state[`${cost}_available`]),
  spend: (state, cost) => { state[`${cost}_available`] = false; },
};
window.IRON_PIT_DICE = {
  rollMany: () => {
    damageRollCalls += 1;
    if (damageRollCalls > 1) throw new Error("Recharge area damage rolled more than once.");
    return [4];
  },
};
const placement = { targetIds: ["first", "second"], origin: [7.5, 27.5], direction: [1, 0] };
window.IRON_PIT_BROWSER_AREA_TARGETING = { legalPlacements: () => [placement] };
window.IRON_PIT_BROWSER_OFFENSE_VALUE = { saveAction: () => 4 };
window.IRON_PIT_BROWSER_FORMATION = {
  targetOrder: () => [],
  chooseRechargeAttack: () => null,
  saveDistance: () => 0,
};
window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION = { resolve: () => { throw new Error("Attack path should not run."); } };
window.IRON_PIT_BROWSER_CHARGE = null;

load("browser-resources.js");
load("browser-saves.js");
load("browser-save-targets.js");
load("browser-recharge-action.js");

const target = (id) => ({
  combatant_id: id,
  side: "heroes",
  position_ft: 10,
  state: {
    current_hp: 20,
    temporary_hp: 0,
    is_alive: true,
    is_dead: false,
    is_unconscious: false,
    is_stable: false,
    death_save_successes: 0,
    death_save_failures: 0,
    action_available: true,
    active_effect_ids: [],
    resources: {},
    template: { name: id, saving_throw_bonuses: { dexterity: 0 } },
  },
});
const action = {
  id: "generic-recharge-area", name: "Generic Recharge Area", saveAbility: "dexterity", dc: 15,
  range: 0, area: { shape: "cone", origin: "self", lengthFt: 15 },
  damageDiceCount: 1, damageDiceSize: 6, damageBonus: 0, damageType: "fire",
  successDamage: "none", resourceId: "area-use", resourceCost: 1,
};
const actor = {
  combatant_id: "actor",
  side: "monsters",
  position_ft: 5,
  state: {
    action_available: true,
    active_effect_ids: [],
    resources: { "area-use": 1 },
    template: {
      id: "generic-recharge-fixture", name: "Recharge Fixture", saving_throw_actions: [action],
      resourceDefinitions: { "area-use": { id: "area-use", maxUses: 1, recharge: { minimumRoll: 5 } } },
    },
  },
};
const first = target("first"), second = target("second");
const setup = { heroes: [first, second], monsters: [actor] };

const choice = window.IRON_PIT_BROWSER_RECHARGE_ACTION.rechargeAreaSaveChoice(actor, setup);
assert.ok(choice);
assert.equal(choice.action.id, action.id);
assert.deepEqual(choice.placement.targetIds, ["first", "second"]);

const result = window.IRON_PIT_BROWSER_RECHARGE_ACTION.resolve(10, 2, actor, setup, "2:actor");
assert.equal(result.handled, true);
assert.equal(result.sequence, 12);
assert.equal(actor.state.action_available, false);
assert.equal(actor.state.resources["area-use"], 0);
assert.equal(damageRollCalls, 1);
assert.equal(result.events[0].save_succeeded, false);
assert.deepEqual(result.events[0].damage_components[0].rolls, [4]);
assert.equal(result.events[0].resource_remaining, 0);
assert.equal(result.events[1].save_succeeded, true);
assert.deepEqual(result.events[1].damage_components, []);
assert.equal(result.events[1].resource_remaining, null);
console.log("Browser Recharge area actions use one cost, one damage roll, and independent saves.");
