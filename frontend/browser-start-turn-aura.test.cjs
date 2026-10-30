"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
window.IRON_PIT_BROWSER_STATE = { distance: (a, b) => Math.abs(a.position_ft - b.position_ft) };
window.IRON_PIT_BROWSER_SAVES = {
  resolveSavingThrow: (_state, ability, dc, magical) => {
    assert.equal(ability, "constitution"); assert.equal(dc, 16); assert.equal(magical, false);
    return { roll: { total: 5 }, succeeded: false };
  },
};
window.IRON_PIT_BROWSER_TIMED = {
  apply: (state, condition, sourceId, options) => {
    state.active_effect_ids.push(condition);
    state.timed_effects.push({ effect_id: condition, source_id: sourceId, source_effect_id: options.sourceEffectId,
      expiry_timing: options.expiryTiming, applied_round: options.appliedRound });
    return condition;
  },
};
window.IRON_PIT_BROWSER_ONGOING_DAMAGE = {};
load("browser-auras.js");

const hezrou = {
  combatant_id: "hezrou", side: "monsters", position_ft: 0,
  state: { is_alive: true, is_dead: false, active_effect_ids: [], template: { name: "Hezrou",
    start_turn_save_condition_auras: [{ id: "stench", name: "Stench", radius_ft: 10,
      save_ability: "constitution", dc: 16, condition: "poisoned", expiry_timing: "target_turn_start",
      magical_effect: false, disabled_while_incapacitated: false }] } },
};
const target = {
  combatant_id: "target", side: "heroes", position_ft: 10,
  state: { is_alive: true, is_dead: false, active_effect_ids: [], timed_effects: [], template: { name: "Target" } },
};
const setup = { heroes: [target], monsters: [hezrou] };
const result = window.IRON_PIT_BROWSER_AURAS.turnStart(1, 3, target, setup);
assert.equal(result.sequence, 2);
assert.equal(result.events.length, 1);
assert.equal(result.events[0].feature_id, "stench");
assert.equal(result.events[0].save_succeeded, false);
assert.deepEqual(result.events[0].applied_condition_ids, ["poisoned"]);
assert.ok(target.state.active_effect_ids.includes("poisoned"));
assert.equal(target.state.timed_effects[0].expiry_timing, "target_turn_start");

target.position_ft = 15; target.state.active_effect_ids = []; target.state.timed_effects = [];
const distant = window.IRON_PIT_BROWSER_AURAS.turnStart(2, 3, target, setup);
assert.equal(distant.events.length, 0);
assert.equal(distant.sequence, 2);

console.log("Browser start-turn save-condition aura parity is enforced.");


const chain = {
  combatant_id: "chain", side: "monsters", position_ft: 0,
  state: {
    is_alive: true, is_dead: false, is_unconscious: false, reaction_available: true,
    active_effect_ids: [], source_effect_immunities: [], active_modifiers: [],
    template: {
      name: "Chain Devil", magic_resistance: false,
      start_turn_save_condition_auras: [{
        id: "unnerving-gaze", name: "Unnerving Gaze", radius_ft: 30,
        save_ability: "wisdom", dc: 15, condition: "frightened",
        expiry_timing: "target_turn_end", magical_effect: false,
        disabled_while_incapacitated: false, success_grants_source_immunity: true,
        requires_source_reaction: true,
      }],
    },
  },
};
const gazeTarget = {
  combatant_id: "gaze-target", side: "heroes", position_ft: 30,
  state: {
    is_alive: true, is_dead: false, is_unconscious: false,
    active_effect_ids: [], source_effect_immunities: [], timed_effects: [],
    template: { name: "Gaze Target", magic_resistance: false, saving_throw_bonuses: { wisdom: 20 } },
  },
};
const gazeSetup = { heroes: [gazeTarget], monsters: [chain] };
const gazeResult = window.IRON_PIT_BROWSER_AURAS.turnStart(10, 1, gazeTarget, gazeSetup);
assert.equal(gazeResult.events.length, 1);
assert.equal(gazeResult.events[0].feature_id, "unnerving-gaze");
assert.equal(chain.state.reaction_available, false);
assert.ok(gazeTarget.state.source_effect_immunities.includes("chain:unnerving-gaze"));

chain.state.reaction_available = true;
const immuneResult = window.IRON_PIT_BROWSER_AURAS.turnStart(11, 2, gazeTarget, gazeSetup);
assert.equal(immuneResult.events.length, 0);
assert.equal(chain.state.reaction_available, true);
