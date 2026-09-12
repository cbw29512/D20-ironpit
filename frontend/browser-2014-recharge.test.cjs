"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

window.IRON_PIT_BROWSER_CONDITION_RULES = { incapacitated: () => false, autoFailStrDex: () => false };
window.IRON_PIT_BROWSER_ATTACK = { adjustedDamage: (_state, amount) => amount, applyDamage: () => null };
window.IRON_PIT_BROWSER_GRAPPLE = { apply: () => [] };
window.IRON_PIT_BROWSER_STATE = { sizeAtMost: () => true };
window.IRON_PIT_BROWSER_BARBARIAN2 = { dangerSenseAdvantage: () => 0 };
window.IRON_PIT_BROWSER_DODGE = { dexSaveAdvantageSources: () => 0 };
window.IRON_PIT_BROWSER_MODIFIERS = { applyD20Bonus: (_state, _kind, roll) => roll };
load("browser-action-economy.js");
load("browser-rolls.js");
load("browser-saves.js");

const E = window.IRON_PIT_ACTION_ECONOMY;
const V = window.IRON_PIT_BROWSER_SAVES;
function dice(values) {
  const queue = [...values];
  window.IRON_PIT_DICE = {
    roll: () => { if (!queue.length) throw new Error("unexpected die roll"); return queue.shift(); },
    rollMany: (count) => Array.from({ length: count }, () => queue.shift()),
  };
}
function member() {
  return {
    combatant_id: "monster-1:breather", side: "monsters", position_ft: 5,
    state: {
      action_available: true, bonus_action_available: true, reaction_available: true,
      turn_terminated: false, is_dead: false, is_unconscious: false,
      active_effect_ids: [], resources: { "fire-breath": 1 },
      template: {
        name: "2014 Breather", ruleset: "2014", traits: [], saving_throw_bonuses: { dexterity: 0 },
        resource_definitions: [{
          id: "fire-breath", name: "Fire Breath", maxUses: 1,
          recharge: { trigger: "start_of_turn", dieSize: 6, minimumRoll: 5 },
        }],
      },
    },
  };
}

{
  const actor = member(); dice([]);
  const full = E.startTurnRecharges(1, 1, actor);
  assert.deepEqual(full.events, []);
  assert.equal(actor.state.resources["fire-breath"], 1);
}
{
  const actor = member(); actor.state.resources["fire-breath"] = 0; dice([4]);
  const failed = E.startTurnRecharges(1, 2, actor);
  assert.equal(failed.events[0].resource_roll.selected_roll, 4);
  assert.equal(failed.events[0].resource_remaining, 0);
  dice([5]);
  const recovered = E.startTurnRecharges(failed.sequence, 3, actor);
  assert.equal(recovered.events[0].resource_roll.selected_roll, 5);
  assert.equal(recovered.events[0].resource_remaining, 1);
}
{
  const actor = member();
  const target = member(); target.combatant_id = "hero-1:target"; target.side = "heroes"; target.state.resources = {};
  const action = {
    id: "fire-breath", name: "Fire Breath", saveAbility: "dexterity", dc: 20, range: 30,
    damageDiceCount: 0, damageDiceSize: 6, damageBonus: 0, successDamage: "none",
    resourceId: "fire-breath", resourceCost: 1,
  };
  dice([10]);
  const event = V.resolveAction(1, 1, actor, target, action, 5);
  assert.equal(event.resource_remaining, 0);
  assert.equal(actor.state.resources["fire-breath"], 0);
  actor.state.action_available = true; dice([10]);
  assert.throws(() => V.resolveAction(2, 1, actor, target, action, 5), /resource is unavailable/);
}

console.log("2014 browser Recharge lifecycle regressions passed.");
