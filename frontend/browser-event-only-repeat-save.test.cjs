"use strict";

// Test the actual shared browser condition and damage-event modules.
// The same immutable condition data works for any named source ability.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
let savesRolled = 0;
window.IRON_PIT_BROWSER_SAVES = {
  resolveSavingThrow(_state, ability, dc) {
    assert.equal(ability, "wisdom");
    assert.equal(dc, 15);
    savesRolled++;
    return { succeeded: true, roll: { total: 20 } };
  },
};
window.IRON_PIT_BROWSER_TIMED = {
  removeGroup(state, effect) {
    state.timed_effects = state.timed_effects.filter((item) => item !== effect);
    state.active_effect_ids = state.active_effect_ids.filter((id) => id !== effect.effect_id);
    return [effect.effect_id];
  },
};
load("browser-condition-lifecycle.js");
load("browser-source-bound-effects.js");

const member = (id) => ({
  combatant_id: id,
  state: {
    template: { name: id, end_turn_condition_removal: null },
    active_effect_ids: [], timed_effects: [],
    is_alive: true, is_dead: false, turns_started: 0,
  },
});
const owner = member("owner");
const victim = member("victim");
const setup = { heroes: [victim], monsters: [owner] };
const effect = {
  effect_id: "charmed", source_id: owner.combatant_id,
  source_effect_id: "renamed-source-control",
  repeat_save_ability: "wisdom", repeat_save_dc: 15,
  repeat_save_timing: null, expiry_timing: null,
  damage_repeat_save_trigger: "any_damage_source",
  repeat_save_failure_count: 0,
};
victim.state.active_effect_ids.push("charmed");
victim.state.timed_effects.push(effect);

try {
  for (const timing of ["target_turn_start", "target_turn_end"]) {
    const turn = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(
      1, 1, victim, timing, setup,
    );
    assert.deepEqual(turn.events, [], "Damage-only control must not roll on turn timing.");
  }
  assert.equal(savesRolled, 0);
  assert.equal(victim.state.active_effect_ids.includes("charmed"), true);

  const reaction = window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS
    .resolveDamageRepeatSaves(2, 1, owner, victim, setup);
  assert.equal(reaction.events.length, 1);
  assert.equal(reaction.events[0].feature_id, "renamed-source-control");
  assert.equal(reaction.events[0].save_succeeded, true);
  assert.equal(savesRolled, 1);
  assert.equal(victim.state.active_effect_ids.includes("charmed"), false);

  const laterTurn = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(
    3, 2, victim, "target_turn_end", setup,
  );
  assert.deepEqual(laterTurn.events, []);
  assert.equal(savesRolled, 1);
} catch (error) {
  console.error("Browser damage-only repeat-save regression failed.", error);
  throw error;
}
console.log("Browser damage-only repeat-save regression passed.");
