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
  available: () => true, spend: () => {},
};
window.IRON_PIT_BROWSER_TIMED_SELF_BUFF_POLICY = { active: () => false };
window.IRON_PIT_BROWSER_ROLLS = {
  modeFromSources: (adv, dis) => adv && !dis ? "advantage" : dis && !adv ? "disadvantage" : "normal",
};
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
load("browser-timed-conditions.js");
load("browser-timed-size-override.js");
load("browser-timed-condition-lifecycle.js");
load("browser-ability-checks.js");
load("browser-timed-self-buffs.js");

const original = { id: "renamed-fighter", name: "Renamed Fighter", size: "medium" };
const state = {
  template: original, active_effect_ids: [], active_modifiers: [],
  timed_effects: [], active_curses: [], replacement_form: null,
};
const member = { combatant_id: "fighter", side: "heroes", state };
const action = {
  id: "growth", name: "Growth", actionCost: "action",
  activationTiming: "action", durationRounds: 10,
  expiryTiming: "source_turn_start", conditionIds: [],
  abilityCheckAdvantageAbilities: ["strength"], sizeOverride: "large",
  savingThrowAdvantageGrants: [], modifierEffects: [],
};
try {
  const event = window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS.resolve(
    1, 1, member, action, { spendActionCost: false },
  );
  assert.equal(event.feature_id, "growth");
  assert.equal(original.size, "medium");
  assert.equal(state.template.size, "large");
  assert.equal(state.timed_effects[0].expires_round, 11);
  assert.equal(state.timed_effects[0].owned_previous_size, "medium");
  const mode = window.IRON_PIT_BROWSER_ABILITY_CHECKS.mode;
  assert.equal(mode(state, 0, 0, { ability: "strength" }), "advantage");
  assert.equal(mode(state, 0, 0, { ability: "dexterity" }), "normal");
  assert.equal(mode(state), "normal");
  assert.deepEqual(window.IRON_PIT_BROWSER_TIMED.removeGroup(state, state.timed_effects[0]), ["growth"]);
  assert.equal(state.template.size, "medium");
  assert.equal(mode(state, 0, 0, { ability: "strength" }), "normal");
  assert.equal(original.size, "medium");
  console.log("Universal browser temporary size/check Advantage lifecycle passed.");
} catch (error) {
  console.error("Universal browser temporary size/check parity failed", error);
  throw error;
}
