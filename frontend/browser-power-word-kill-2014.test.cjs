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
  "browser-modifiers.js",
  "browser-zero-hp-replacement.js",
  "browser-zero-hp.js",
  "browser-action-economy.js",
  "browser-formation.js",
  "browser-hp-threshold-instant-death.js",
]) load(file);

window.IRON_PIT_BROWSER_STATE = {
  effectiveMaxHp: (state) => state.template.max_hp,
  distance: (a, b) => Math.abs(a.position_ft - b.position_ft),
};
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS = { endDamageSensitive: () => {} };

function member(id, side, hp) {
  return {
    combatant_id: id,
    side,
    position_ft: side === "heroes" ? 0 : 30,
    state: {
      template: {
        id, name: id, kind: "character", ruleset: "2014", max_hp: 200, size: "medium",
        speed_ft: 30, traits: [], condition_immunities: [],
        hp_threshold_instant_death_actions: [],
      },
      current_hp: hp, temporary_hp: 0, is_alive: true, is_dead: false,
      is_unconscious: false, is_stable: false,
      death_save_successes: 0, death_save_failures: 0,
      action_available: true, bonus_action_available: true, reaction_available: true,
      active_effect_ids: [], active_buff_effect_ids: [], active_modifiers: [],
      pending_zero_hp_replacement_logs: [], concentration: null,
      resources: {}, grapple_sources: [],
    },
  };
}

const varek = member("Varek", "heroes", 100);
varek.state.template.hp_threshold_instant_death_actions = [{
  id: "power-word-kill", name: "Power Word Kill", actionCost: "action",
  range: 60, maxCurrentHp: 100, resourceId: "mystic-arcanum-9",
  resourceCost: 1, magicalEffect: true, animation: "instant-death",
}];
varek.state.resources["mystic-arcanum-9"] = 1;
const target = member("Target", "monsters", 101);
const setup = { heroes: [varek], monsters: [target] };
const P = window.IRON_PIT_BROWSER_HP_THRESHOLD_INSTANT_DEATH;

assert.equal(P.choose(varek, setup), null);
target.state.current_hp = 100;
const selected = P.choose(varek, setup);
assert.ok(selected);
const event = P.resolve(1, 1, varek, target, selected.action, setup);
assert.equal(event.feature_id, "power-word-kill");
assert.equal(event.resource_remaining, 0);
assert.equal(target.state.is_dead, true);
assert.equal(target.state.current_hp, 0);

const wardedVarek = member("Varek2", "heroes", 100);
wardedVarek.state.template.hp_threshold_instant_death_actions = varek.state.template.hp_threshold_instant_death_actions;
wardedVarek.state.resources["mystic-arcanum-9"] = 1;
const warded = member("Warded", "monsters", 100);
warded.state.active_buff_effect_ids = ["death-ward"];
warded.state.active_modifiers = [{
  id: "cleric:death-ward:warded:0", source_id: "cleric", source_effect_id: "death-ward",
  source_name: "Death Ward", source_is_magical: true, kind: "zero-hp-replacement",
  replacement_hp: 1, prevents_instant_death: true,
}];
const wardedSetup = { heroes: [wardedVarek], monsters: [warded] };
const wardedEvent = P.resolve(
  1, 1, wardedVarek, warded,
  wardedVarek.state.template.hp_threshold_instant_death_actions[0], wardedSetup,
);
assert.equal(wardedEvent.resource_remaining, 0);
assert.equal(warded.state.is_dead, false);
assert.equal(warded.state.current_hp, 100);
assert.equal(warded.state.active_modifiers.length, 0);
assert.match(wardedEvent.description, /negates the instant-death effect/);

console.log("2014 Power Word Kill browser regression passed.");
