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
// This mock mirrors the shared, source-neutral condition immunity contract.
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = {
  immune: (state, conditionId) => (state.template.condition_immunities || []).includes(conditionId),
};
window.IRON_PIT_BROWSER_STATE = {
  distance: (left, right) => Math.abs(left.position_ft - right.position_ft),
};
window.IRON_PIT_BROWSER_SAVING_THROWS = {
  resolveSavingThrow: (_state, _ability, dc) => ({ roll: 1, succeeded: false, dc }),
};
window.IRON_PIT_BROWSER_TIMED = {
  apply: (state, effectId, sourceId, options) => {
    state.timed_effects = state.timed_effects || [];
    state.timed_effects.push({ effect_id: effectId, source_id: sourceId, expiry_timing: options.expiryTiming });
    state.active_effect_ids = [...(state.active_effect_ids || []), effectId];
    return effectId;
  },
};

load("browser-turn-start-save-condition-reaction.js");
const R = window.IRON_PIT_BROWSER_TURN_START_SAVE_CONDITION_REACTION;

function member(id, name, position, reaction = null) {
  return {
    combatant_id: id,
    position_ft: position,
    side: reaction ? "monsters" : "heroes",
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

// A condition-immune target never receives the debuff and the source retains its Reaction.
const immuneHero = member("immune", "Immune Hero", 10);
immuneHero.state.template.condition_immunities = ["frightened"];
const devil3 = member("devil3", "Chain Devil", 0, reaction);
const immuneResult = R.resolve(1, 1, immuneHero, { heroes: [immuneHero], monsters: [devil3] });
assert.equal(immuneResult.events.length, 0);
assert.equal(immuneHero.state.active_effect_ids.includes("frightened"), false);
assert.equal(devil3.state.reaction_available, true);

// Missing universal effect support must fail closed, never log a phantom condition.
const savedTimed = window.IRON_PIT_BROWSER_TIMED;
window.IRON_PIT_BROWSER_TIMED = undefined;
const devil4 = member("devil4", "Chain Devil", 0, reaction);
const hero4 = member("hero4", "Hero", 10);
assert.throws(
  () => R.resolve(1, 1, hero4, { heroes: [hero4], monsters: [devil4] }),
  /Universal timed conditions are required/,
);
assert.equal(devil4.state.reaction_available, true, "missing engine must not consume the Reaction");
assert.equal(hero4.state.active_effect_ids.length, 0, "missing engine must not mutate target conditions");
window.IRON_PIT_BROWSER_TIMED = savedTimed;

// The AI must preserve its Reaction for enemies, never target same-side allies.
const friendly = member("friendly", "Friendly Devil", 5);
friendly.side = "monsters";
const devil5 = member("devil5", "Chain Devil", 0, reaction);
const friendlyResult = R.resolve(1, 1, friendly, { heroes: [], monsters: [devil5, friendly] });
assert.equal(friendlyResult.events.length, 0);
assert.equal(devil5.state.reaction_available, true);

console.log("browser turn-start save-condition reaction tests passed");
