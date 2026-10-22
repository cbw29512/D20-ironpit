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
window.IRON_PIT_BROWSER_SAVES = { resolveAction: (sequence, _round, _source, victim) => {
  victim.state.current_hp -= 4;
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
const second = window.IRON_PIT_BROWSER_DEATH_TRIGGER_DISPATCH.resolvePending(first.sequence, 2, setup);
assert.equal(second.events.length, 0);
assert.throws(() => window.IRON_PIT_BROWSER_DEATH_TRIGGER_DISPATCH.declaredActions({
  state: { template: { id: "broken", death_trigger_effect_ids: ["missing"],
    death_trigger_actions: [] } },
}), /Unbound browser Death Trigger/);
console.log("Browser source-declared Death Trigger dispatch verified");
