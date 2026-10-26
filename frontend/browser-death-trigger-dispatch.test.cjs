"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");
global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
load("browser-death-trigger-rules.js");
const action = { id: "burst", name: "Burst", saveAbility: "dexterity", dc: 10,
  range: 5, damageDiceCount: 1, damageDiceSize: 6, damageBonus: 0,
  damageType: "fire", successDamage: "none", targetScope: "all-other-creatures" };
const member = (id, dead, position) => ({ combatant_id: id, position_ft: position,
  state: { is_dead: dead, is_alive: !dead, current_hp: dead ? 0 : 10,
    active_buff_effect_ids: dead ? ["death-trigger"] : [], feature_use_counts: {},
    template: { id, name: id, death_trigger_effect_ids: dead ? ["burst"] : [],
      death_trigger_actions: dead ? [action] : [] } } });
const source = member("source", true, 0), target = member("target", false, 5);
window.IRON_PIT_BROWSER_STATE = { distance: (a, b) => Math.abs(a.position_ft - b.position_ft) };
window.IRON_PIT_DICE = { rollMany: () => [4] };
let lastAction = null;
window.IRON_PIT_BROWSER_SAVES = { resolveAction: (sequence, _round, _source, victim, actionArg) => {
  lastAction = actionArg;
  victim.state.current_hp -= actionArg.damageDiceCount ? 4 : 0;
  if (victim.state.current_hp <= 0) {
    victim.state.current_hp = 0;
    victim.state.is_alive = false;
    victim.state.is_dead = true;
  }
  return { sequence, event_type: "saving_throw", target_id: victim.combatant_id };
} };
window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH = {
  chain: (sequence, _round, _source, event) => ({ events: [event], sequence }),
};
load("browser-death-trigger-dispatch.js");
const setup = { heroes: [target], monsters: [source] };
const first = window.IRON_PIT_BROWSER_DEATH_TRIGGER_DISPATCH.resolvePending(1, 2, setup);
assert.equal(first.events.length, 1);
assert.equal(target.state.current_hp, 6);
assert.equal(source.state.feature_use_counts["death-trigger"], 1);
const conditionAction = { id: "dust-burst", name: "Dust Burst", saveAbility: "constitution",
  dc: 10, range: 5, damageDiceCount: 0, damageDiceSize: 6, damageBonus: 0,
  damageType: null, successDamage: "none", targetScope: "all-other-creatures",
  failedSaveTimedEffect: { effectId: "blinded", durationRounds: 10,
    expiryTiming: "target_turn_end", repeatSaveAbility: "constitution",
    repeatSaveDc: 10, repeatSaveTiming: "target_turn_end" } };
const conditionSource = member("condition-source", true, 0);
conditionSource.state.template.death_trigger_effect_ids = ["dust-burst"];
conditionSource.state.template.death_trigger_actions = [conditionAction];
const conditionResult = window.IRON_PIT_BROWSER_DEATH_TRIGGER_DISPATCH.resolvePending(
  first.sequence, 2, { heroes: [target], monsters: [conditionSource] },
);
assert.equal(conditionResult.events.length, 1);
assert.equal(lastAction.failedSaveTimedEffect.effectId, "blinded");
assert.equal(lastAction.failedSaveTimedEffect.repeatSaveTiming, "target_turn_end");
const second = window.IRON_PIT_BROWSER_DEATH_TRIGGER_DISPATCH.resolvePending(first.sequence, 2, setup);
assert.equal(second.events.length, 0);

const chainSource = member("source", true, 0);
const chainMiddle = member("chain-middle", false, 5);
const chainTarget = member("chain-target", false, 10);
chainMiddle.state.current_hp = 4;
chainMiddle.state.active_buff_effect_ids = ["death-trigger"];
chainMiddle.state.template.death_trigger_effect_ids = ["burst"];
chainMiddle.state.template.death_trigger_actions = [action];
const chained = window.IRON_PIT_BROWSER_DEATH_TRIGGER_DISPATCH.resolvePending(
  second.sequence, 3, { heroes: [chainTarget], monsters: [chainSource, chainMiddle] },
);
assert.equal(chained.events.length, 2);
assert.equal(chainMiddle.state.is_dead, true);
assert.equal(chainTarget.state.current_hp, 6);
assert.notEqual(chainSource, source);
assert.equal(chainSource.state.feature_use_counts["death-trigger"], 1);
assert.equal(chainMiddle.state.feature_use_counts["death-trigger"], 1);

assert.throws(() => window.IRON_PIT_BROWSER_DEATH_TRIGGER_DISPATCH.declaredActions({
  state: { template: { id: "broken", death_trigger_effect_ids: ["missing"],
    death_trigger_actions: [] } },
}), /Unbound browser Death Trigger/);
console.log("Browser source-declared Death Trigger dispatch verified");
