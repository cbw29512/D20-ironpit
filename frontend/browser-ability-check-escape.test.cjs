"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "action" && state.action_available,
  spend: (state) => { state.action_available = false; },
};
window.IRON_PIT_BROWSER_ROLLS = {
  d20: (bonus) => ({ total: 20 + (bonus || 0), selected_roll: 20, modifier: bonus || 0, rolls: [20] }),
  modeFromSources: () => "normal",
};
window.IRON_PIT_BROWSER_ABILITY_CHECKS = {
  mode: () => "normal",
  resolve: (_state, _ability, roll, dc) => ({ roll, succeeded: roll.total >= dc }),
};
window.IRON_PIT_BROWSER_TIMED = {
  removeEffect: (state, effect) => {
    state.timed_effects = state.timed_effects.filter((item) => item !== effect);
    state.active_effect_ids = state.active_effect_ids.filter((id) => id !== effect.effect_id);
  },
};

load("browser-ability-check-escape.js");

const actor = {
  combatant_id: "hero",
  state: {
    template: {
      name: "Hero",
      ability_scores: { strength: 16, dexterity: 14, constitution: 14, intelligence: 10, wisdom: 10, charisma: 10 },
    },
    action_available: true,
    active_effect_ids: ["restrained"],
    timed_effects: [{
      effect_id: "restrained",
      escape_check_ability: "strength",
      escape_check_dc: 14,
    }],
  },
};

assert.equal(window.IRON_PIT_BROWSER_ABILITY_CHECK_ESCAPE.shouldEscape(actor.state), true);
const event = window.IRON_PIT_BROWSER_ABILITY_CHECK_ESCAPE.resolve(1, 1, actor, { heroes: [actor], monsters: [] });
assert.equal(event.feature_id, "escape-check");
assert.equal(event.check_succeeded, true);
assert.equal(actor.state.action_available, false);
assert.deepEqual(actor.state.active_effect_ids, []);
console.log("Action Strength-check escape ended Restrained.");
