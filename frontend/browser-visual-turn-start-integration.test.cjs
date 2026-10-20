"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = name => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"));
load("browser-staged-save-debuff.js");
load("browser-turn-start-visual-policy.js");
load("browser-visual-source-aversion.js");
const operations = [];
const member = (id, rule = null) => ({
  combatant_id: id, side: id === "victim" ? "heroes" : "monsters",
  state: { template: { name: id, visualTurnStartRule: rule }, current_hp: 10,
    is_dead: false, is_surprised: false, turns_started: 1, timed_effects: [], active_effect_ids: [] },
});
const rule = { sourceId: "visual", sourceName: "Gaze", rangeFt: 30, saveDc: 12 };
const source = member("source", rule), victim = member("victim");
const setup = { heroes: [victim], monsters: [source] };
window.IRON_PIT_BROWSER_STATE = { distance: () => 10 };
window.IRON_PIT_BROWSER_CONDITION_RULES = { incapacitated: () => false, canSee: () => true };
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_SAVING_THROWS = { resolveSavingThrow: () => ({ roll: { total: 4 }, succeeded: false }) };
window.IRON_PIT_BROWSER_TIMED = {
  apply: (state, id, sourceId, opts) => {
    operations.push(["apply", id]);
    state.timed_effects.push({ effect_id: id, source_id: sourceId, source_effect_id: opts.sourceEffectId });
    if (!state.active_effect_ids.includes(id)) state.active_effect_ids.push(id);
    return id;
  },
  removeEffect: (state, effect) => {
    operations.push(["remove", effect.effect_id]);
    state.timed_effects = state.timed_effects.filter(x => x !== effect);
    state.active_effect_ids = state.active_effect_ids.filter(id => id !== effect.effect_id);
  },
};
load("browser-visual-turn-start-integration.js");
const bridge = window.IRON_PIT_BROWSER_VISUAL_TURN_START_INTEGRATION;
const context = { member: victim, setup, sequence: 0, round: 1, initiative: { turn_order: ["victim", "source"] } };
let result = bridge.resolve(context);
assert.match(result.events[0].description, /averts its eyes/);
assert.equal(victim.state.timed_effects.length, 0);
assert.equal(victim.state.visual_aversion_windows.length, 1);
context.initiative.turn_order = ["source", "victim"];
result = bridge.resolve(context);
assert.deepEqual(operations, [["apply", "restrained"]]);
assert.equal(result.events[0].save_dc, 12);
result = bridge.resolve(context);
assert.deepEqual(operations, [["apply", "restrained"], ["remove", "restrained"], ["apply", "petrified"]]);
window.IRON_PIT_BROWSER_SAVING_THROWS.resolveSavingThrow = () => ({ roll: { total: 12 }, succeeded: true });
result = bridge.resolve(context);
assert.equal(result.events[0].save_succeeded, true);
// A granted save-success override must prevail over the raw failed total.
operations.length = 0;
victim.state.timed_effects = [];
window.IRON_PIT_BROWSER_SAVING_THROWS.resolveSavingThrow = () => ({ roll: { total: 2 }, succeeded: true });
result = bridge.resolve(context);
assert.equal(result.events[0].save_succeeded, true);
assert.deepEqual(operations, []);
// Competing gaze sources resolve highest initiative first, independent of array order.
const second = member("second", rule);
source.state.initiative_total = 99; // deliberately contradict canonical order
second.state.initiative_total = 3;
victim.state.timed_effects = [];
window.IRON_PIT_BROWSER_SAVING_THROWS.resolveSavingThrow = () => ({ roll: { total: 12 }, succeeded: true });
const ordered = bridge.resolve({
  ...context, setup: { heroes: [victim], monsters: [source, second] },
  initiative: { turn_order: ["second", "source", "victim"] },
});
assert.equal(ordered.events[0].actor_id, "second");
assert.equal(ordered.events[1].actor_id, "source");
console.log("Visual turn-start combat bridge checks passed.");

assert.throws(() => bridge.resolve({ ...context, initiative: null }), /requires resolved initiative/);
