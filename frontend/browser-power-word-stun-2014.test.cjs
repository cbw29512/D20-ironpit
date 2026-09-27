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

for (const file of [
  "browser-condition-immunity.js",
  "browser-timed-conditions.js",
  "browser-action-economy.js",
  "browser-formation.js",
  "browser-hp-threshold-condition.js",
]) load(file);

function member(id, side, hp) {
  return {
    combatant_id: id,
    side,
    position_ft: side === "heroes" ? 0 : 30,
    state: {
      template: {
        name: id,
        ruleset: "2014",
        size: "medium",
        speed_ft: 30,
        movement_modes: { walk_ft: 30, fly_ft: 0, climb_ft: 0, swim_ft: 0, burrow_ft: 0, hover: false },
        hp_threshold_condition_actions: [],
      },
      current_hp: hp,
      is_alive: true,
      is_dead: false,
      action_available: true,
      bonus_action_available: true,
      reaction_available: true,
      active_effect_ids: [],
      timed_effects: [],
      active_modifiers: [],
      resources: {},
      grapple_sources: [],
    },
  };
}

const varek = member("Varek", "heroes", 100);
varek.state.template.hp_threshold_condition_actions = [{
  id: "power-word-stun",
  name: "Power Word Stun",
  actionCost: "action",
  range: 60,
  maxCurrentHp: 150,
  conditionId: "stunned",
  repeatSaveAbility: "constitution",
  repeatSaveDc: 18,
  repeatSaveTiming: "target_turn_end",
  resourceId: "mystic-arcanum-8",
  resourceCost: 1,
  magicalEffect: true,
  animation: "spell-condition",
}];
varek.state.resources["mystic-arcanum-8"] = 1;

const target = member("Target", "monsters", 151);
const setup = { heroes: [varek], monsters: [target] };
window.IRON_PIT_BROWSER_STATE = { distance: (a, b) => Math.abs(a.position_ft - b.position_ft) };
const P = window.IRON_PIT_BROWSER_HP_THRESHOLD_CONDITION;

assert.equal(P.choose(varek, setup), null);
target.state.current_hp = 150;
const selected = P.choose(varek, setup);
assert.ok(selected);
assert.equal(selected.action.id, "power-word-stun");

const event = P.resolve(1, 1, varek, target, selected.action, setup);
assert.equal(event.feature_id, "power-word-stun");
assert.equal(event.resource_remaining, 0);
assert.equal(varek.state.action_available, false);
assert.ok(target.state.active_effect_ids.includes("stunned"));
assert.equal(target.state.timed_effects[0].repeat_save_ability, "constitution");
assert.equal(target.state.timed_effects[0].repeat_save_dc, 18);
assert.equal(target.state.timed_effects[0].repeat_save_timing, "target_turn_end");

console.log("2014 Power Word Stun browser regression passed.");
