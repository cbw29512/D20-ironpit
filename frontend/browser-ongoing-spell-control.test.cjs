"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
load("browser-rolls.js");
window.IRON_PIT_BROWSER_MODIFIERS = { applyD20Bonus: (_state, _kind, roll) => roll };
window.IRON_PIT_BROWSER_CONDITION_RULES = { autoFailStrDex: () => false };
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
load("browser-saves.js");
load("browser-timed-conditions.js");
load("browser-condition-lifecycle.js");
load("browser-ongoing-spell-control.js");

function target() {
  return {
    combatant_id: "fighter",
    state: {
      template: { name: "Fighter", saving_throw_bonuses: { wisdom: 2 } },
      active_effect_ids: [], timed_effects: [], active_modifiers: [], is_unconscious: false,
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
    member.state, "frightened", "shaman", "fear", "wisdom", 30, { appliedRound: 1 },
  );
  window.IRON_PIT_DICE = { roll: () => 1 };
  const result = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(1, 1, member, "target_turn_end");
  assert.equal(result.events[0].save_succeeded, false);
  assert.deepEqual(result.events[0].removed_condition_ids, []);
  assert.deepEqual(member.state.active_effect_ids, ["frightened"]);
  assert.equal(member.state.timed_effects.length, 1);
}

console.log("Browser ongoing spell control repeat-save regression passed.");
