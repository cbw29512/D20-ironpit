"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

for (const file of [
  "browser-condition-immunity.js",
  "browser-condition-rules.js",
  "browser-action-economy.js",
  "browser-timed-conditions.js",
  "browser-modifiers.js",
  "browser-concentration.js",
  "browser-owner-action-expiry.js",
  "browser-timed-self-buffs.js",
]) load(file);

const state = {
  template: { name: "Source", condition_immunities: [] },
  current_hp: 20,
  is_alive: true,
  is_dead: false,
  is_unconscious: false,
  action_available: true,
  bonus_action_available: true,
  active_effect_ids: [],
  timed_effects: [],
  active_modifiers: [],
  concentration: null,
  resources: {},
};
const member = {
  combatant_id: "source",
  side: "monsters",
  state,
  position_ft: 0,
};
const enemy = {
  combatant_id: "target",
  side: "heroes",
  state: {
    ...structuredClone(state),
    template: { name: "Target", condition_immunities: [] },
  },
  position_ft: 5,
};
const setup = { heroes: [enemy], monsters: [member] };
const action = {
  id: "self-invisibility",
  name: "Invisibility",
  actionCost: "action",
  resourceId: null,
  resourceCost: 1,
  durationRounds: 600,
  conditionIds: ["invisible"],
  concentration: true,
  endsOnOwnerAttack: true,
  endsOnOwnerSpellCast: true,
  priority: 70,
  animation: "invisibility",
};

const event = window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS.resolve(1, 1, member, action, setup);
assert.equal(event.feature_id, action.id);
assert.ok(state.active_effect_ids.includes("invisible"));
assert.equal(state.concentration.effect_id, action.id);
assert.equal(state.timed_effects[0].ends_on_owner_attack, true);
assert.equal(state.timed_effects[0].ends_on_owner_spell_cast, true);

const removed = window.IRON_PIT_BROWSER_OWNER_ACTION_EXPIRY.expire(
  state, "attack", [state, enemy.state],
);
assert.deepEqual(removed, ["invisible"]);
assert.ok(!state.active_effect_ids.includes("invisible"));
assert.equal(state.concentration, null);

console.log("Browser timed self-buff Invisibility regression passed.");
