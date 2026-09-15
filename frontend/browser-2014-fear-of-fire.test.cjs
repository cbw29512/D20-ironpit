const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_MODIFIERS = {
  attacksAgainstAdvantage: () => 0, effectiveSpeed: () => 30, expireTargetTurn: () => {},
};
window.IRON_PIT_BROWSER_BARBARIAN2 = { attacksAgainstAdvantage: () => 0 };
window.IRON_PIT_BROWSER_GRAPPLE = { attackDisadvantage: () => 0, speedIsZero: () => false };
window.IRON_PIT_BROWSER_CONDITION_RULES = {
  attackAdvantage: () => 0, has: (state, id) => state.active_effect_ids.includes(id), incapacitated: () => false,
};
window.IRON_PIT_BROWSER_SOURCE_EFFECT_IMMUNITY = { grant: () => {} };
window.IRON_PIT_BROWSER_SAVES = { resolveSavingThrow: () => { throw new Error("unexpected save"); } };
load("browser-timed-conditions.js");
load("browser-damage-triggered-effects.js");
load("browser-attack.js");
load("browser-condition-lifecycle.js");

function state() {
  return {
    template: {
      name: "Yeti", ruleset: "2014", armor_class: 12, speed_ft: 40,
      damageTriggeredRollPenalties: [{
        id: "fear-of-fire", damageTypes: ["fire"], attackRollDisadvantage: true,
        abilityCheckDisadvantage: true, expiresAfterNextTargetTurn: true,
      }],
    },
    current_hp: 51, active_effect_ids: [], timed_effects: [], active_modifiers: [],
    is_alive: true, is_dead: false, is_unconscious: false, grapple_sources: [],
  };
}

{
  const yeti = state();
  assert.deepEqual(window.IRON_PIT_BROWSER_DAMAGE_TRIGGERED_EFFECTS.apply(yeti, 5, ["cold"]), []);
  assert.equal(yeti.timed_effects.length, 0);
  assert.deepEqual(window.IRON_PIT_BROWSER_DAMAGE_TRIGGERED_EFFECTS.apply(yeti, 5, ["fire"]), ["fear-of-fire"]);
  assert.equal(window.IRON_PIT_BROWSER_TIMED.attackRollDisadvantage(yeti), 1);
  assert.equal(window.IRON_PIT_BROWSER_TIMED.abilityCheckDisadvantage(yeti), 1);
  const defender = state(); defender.template.name = "Target";
  assert.equal(window.IRON_PIT_BROWSER_ATTACK.conditionSources(yeti, defender, 5, "target").disadvantage, 1);
}

{
  const yeti = state(); window.IRON_PIT_BROWSER_DAMAGE_TRIGGERED_EFFECTS.apply(yeti, 5, ["fire"]);
  const member = { combatant_id: "yeti", state: yeti };
  let result = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(1, 1, member, "target_turn_start");
  assert.equal(result.events.length, 0);
  result = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(result.sequence, 1, member, "target_turn_end");
  assert.equal(result.events.length, 1); assert.equal(yeti.active_effect_ids.includes("fear-of-fire"), false);
}

{
  const yeti = state(); window.IRON_PIT_BROWSER_DAMAGE_TRIGGERED_EFFECTS.apply(yeti, 5, ["fire"]);
  const member = { combatant_id: "yeti", state: yeti };
  let result = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(1, 1, member, "target_turn_end");
  assert.equal(result.events.length, 0); assert.equal(yeti.active_effect_ids.includes("fear-of-fire"), true);
  result = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(result.sequence, 2, member, "target_turn_start");
  result = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(result.sequence, 2, member, "target_turn_end");
  assert.equal(result.events.length, 1); assert.equal(yeti.active_effect_ids.includes("fear-of-fire"), false);
}

console.log("browser 2014 Fear of Fire regression passed");
