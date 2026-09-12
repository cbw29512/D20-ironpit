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
load("browser-source-effect-immunity.js");
load("browser-save-control-effects.js");
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
      active_effect_ids: [], resources: { "fire-breath": 1 }, source_effect_immunities: [],
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
  E.spend(actor.state, "action");
  assert.equal(actor.state.action_available, false);
}

{
  const actor = member();
  const action = { id: "fire-breath", name: "Fire Breath", saveAbility: "dexterity", dc: 11, range: 30,
    damageDiceCount: 0, damageDiceSize: 6, damageBonus: 0, damageType: null, successDamage: "none",
    resourceId: "fire-breath", resourceCost: 1 };
  const target = member(); target.combatant_id = "hero-1:target"; target.side = "heroes";
  dice([20]);
  const event = V.resolveAction(1, 1, actor, target, action, 10);
  assert.equal(event.save_succeeded, true);
  assert.equal(actor.state.resources["fire-breath"], 0);
  assert.equal(event.resource_remaining, 0);
  assert.equal(actor.state.action_available, false);
}

console.log("2014 browser Recharge regressions passed.");
