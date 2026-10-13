"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "reaction" && state.reaction_available && !state.is_dead,
  spend: (state, cost) => {
    if (cost !== "reaction" || !state.reaction_available) throw new Error("Reaction unavailable.");
    state.reaction_available = false;
  },
};
window.IRON_PIT_BROWSER_CONDITION_RULES = {
  has: (state, id) => (state.active_effect_ids || []).includes(id),
  canSee: () => true,
};
window.IRON_PIT_BROWSER_STATE = {
  distance: (left, right) => Math.abs(left.position_ft - right.position_ft),
};
window.IRON_PIT_BROWSER_SAVING_THROWS = {
  resolveSavingThrow: (_state, _ability, dc) => ({ roll: 1, succeeded: false, dc }),
};
window.IRON_PIT_BROWSER_TIMED_CONDITIONS = {
  apply: (state, effectId, sourceId, options) => {
    state.timed_effects = state.timed_effects || [];
    state.timed_effects.push({ effect_id: effectId, source_id: sourceId, expiry_timing: options.expiryTiming });
    state.active_effect_ids = [...(state.active_effect_ids || []), effectId];
  },
};

load("browser-turn-start-save-condition-reaction.js");
const R = window.IRON_PIT_BROWSER_TURN_START_SAVE_CONDITION_REACTION;

function member(id, name, position, reaction = null) {
  return {
    combatant_id: id,
    position_ft: position,
    state: {
      is_alive: true,
      is_dead: false,
      reaction_available: true,
      active_effect_ids: [],
      timed_effects: [],
      template: {
        name,
        turnStartSaveConditionReaction: reaction,
      },
    },
  };
}

const reaction = {
  sourceId: "unnerving-mask",
  sourceName: "Unnerving Mask",
  rangeFt: 30,
  saveAbility: "wisdom",
  saveDc: 14,
  conditionId: "frightened",
  expiryTiming: "target_turn_end",
  requiresSourceCanSeeTarget: true,
  requiresTargetCanSeeSource: true,
};

const devil = member("devil", "Chain Devil", 0, reaction);
const hero = member("hero", "Hero", 10);
const setup = { heroes: [hero], monsters: [devil] };

const result = R.resolve(1, 1, hero, setup);
assert.equal(result.events.length, 1);
assert.equal(result.events[0].save_succeeded, false);
assert.deepEqual(result.events[0].applied_condition_ids, ["frightened"]);
assert.equal(devil.state.reaction_available, false);
assert.equal(hero.state.active_effect_ids.includes("frightened"), true);
assert.equal(hero.state.timed_effects[0].expiry_timing, "target_turn_end");

// Out of range
const far = member("far", "Far Hero", 40);
const devil2 = member("devil2", "Chain Devil", 0, reaction);
const farResult = R.resolve(1, 1, far, { heroes: [far], monsters: [devil2] });
assert.equal(farResult.events.length, 0);
assert.equal(devil2.state.reaction_available, true);

console.log("browser turn-start save-condition reaction tests passed");
