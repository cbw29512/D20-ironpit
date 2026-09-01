"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
load("browser-rolls.js");
window.IRON_PIT_BROWSER_MODIFIERS = {
  applyD20Bonus: (_state, _kind, roll) => roll,
  removeSource: () => {},
};
window.IRON_PIT_BROWSER_CONDITION_RULES = { autoFailStrDex: () => false, incapacitated: (state) => Boolean(state.is_unconscious) };
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
load("browser-saves.js");
load("browser-timed-conditions.js");
load("browser-condition-lifecycle.js");
load("browser-ongoing-spell-control.js");
load("browser-concentration.js");

function target(name = "Fighter") {
  return {
    combatant_id: name.toLowerCase(),
    state: {
      template: { name, saving_throw_bonuses: { wisdom: 2, constitution: 2 } },
      active_effect_ids: [], timed_effects: [], active_modifiers: [], concentration: null,
      is_dead: false, is_unconscious: false,
    },
  };
}

{
  const member = target();
  window.IRON_PIT_BROWSER_ONGOING_SPELL_CONTROL.apply(
    member.state, "frightened", "shaman", "fear", "wisdom", 13, { appliedRound: 1 },
  );
  assert.deepEqual(member.state.active_effect_ids, ["frightened"]);
  const effect = member.state.timed_effects[0];
  assert.equal(effect.source_effect_id, "fear");
  assert.equal(effect.repeat_save_ability, "wisdom");
  assert.equal(effect.repeat_save_dc, 13);
  assert.equal(effect.repeat_save_timing, "target_turn_end");

  window.IRON_PIT_DICE = { roll: () => 20 };
  const result = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(1, 1, member, "target_turn_end");
  assert.equal(result.events.length, 1);
  assert.equal(result.events[0].save_succeeded, true);
  assert.deepEqual(result.events[0].removed_condition_ids, ["frightened"]);
  assert.deepEqual(member.state.active_effect_ids, []);
  assert.deepEqual(member.state.timed_effects, []);
}

{
  const member = target();
  window.IRON_PIT_BROWSER_ONGOING_SPELL_CONTROL.apply(
    member.state, "frightened", "shaman", "fear", "wisdom", 30, { appliedRound: 1, turnBehavior: "forced_retreat" },
  );
  assert.equal(window.IRON_PIT_BROWSER_ONGOING_SPELL_CONTROL.forcedRetreatActive(member.state), true);
  window.IRON_PIT_DICE = { roll: () => 1 };
  const result = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(1, 1, member, "target_turn_end");
  assert.equal(result.events[0].save_succeeded, false);
  assert.deepEqual(result.events[0].removed_condition_ids, []);
  assert.deepEqual(member.state.active_effect_ids, ["frightened"]);
  assert.equal(member.state.timed_effects.length, 1);
}

{
  const caster = target("Shaman"), member = target();
  const states = [caster.state, member.state];
  window.IRON_PIT_BROWSER_CONCENTRATION.start(caster.state, "shaman", "fear", 1, states, 11);
  window.IRON_PIT_BROWSER_ONGOING_SPELL_CONTROL.apply(
    member.state, "frightened", "shaman", "fear", "wisdom", 13,
    { appliedRound: 1, turnBehavior: "forced_retreat" },
  );
  assert.equal(window.IRON_PIT_BROWSER_ONGOING_SPELL_CONTROL.forcedRetreatActive(member.state), true);
  assert.equal(window.IRON_PIT_BROWSER_CONCENTRATION.end(caster.state, states), true);
  assert.deepEqual(member.state.timed_effects, []);
  assert.deepEqual(member.state.active_effect_ids, []);
  assert.equal(window.IRON_PIT_BROWSER_ONGOING_SPELL_CONTROL.forcedRetreatActive(member.state), false);
}

console.log("Browser ongoing spell control regression passed.");
