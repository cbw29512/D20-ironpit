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
  "browser-damage-defense-rules.js",
  "browser-hp-threshold-instant-death.js",
]) load(file);

window.IRON_PIT_BROWSER_STATE = {
  effectiveMaxHp: (state) => state.template.max_hp,
  distance: (a, b) => Math.abs(a.position_ft - b.position_ft),
};
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS = { endDamageSensitive: () => {} };
window.IRON_PIT_DICE = { rollMany: (count) => Array(count).fill(1) };

function member(id, side, hp) {
  return {
    combatant_id: id,
    side,
    position_ft: side === "heroes" ? 0 : 30,
    state: {
      template: {
        id, name: id, kind: "character", ruleset: "2024", max_hp: 200, size: "medium",
        speed_ft: 30, traits: [], condition_immunities: [],
        damage_resistances: [], damage_vulnerabilities: [], damage_immunities: [],
        conditional_damage_defenses: [],
        hp_threshold_instant_death_actions: [],
      },
      current_hp: hp, temporary_hp: 0, is_alive: true, is_dead: false,
      is_unconscious: false, is_stable: false,
      death_save_successes: 0, death_save_failures: 0,
      action_available: true, bonus_action_available: true, reaction_available: true,
      active_effect_ids: [], active_buff_effect_ids: [], active_modifiers: [],
      active_conditional_damage_defenses: [], temporary_damage_resistances: [], timed_effects: [],
      pending_zero_hp_replacement_logs: [], concentration: null,
      resources: {}, grapple_sources: [],
    },
  };
}

const action = {
  id: "power-word-kill", name: "Power Word Kill", actionCost: "action",
  range: 60, maxCurrentHp: 100,
  fallbackDamageDiceCount: 12, fallbackDamageDiceSize: 12,
  fallbackDamageBonus: 0, fallbackDamageType: "psychic",
  resourceId: "spell-slot-9", resourceCost: 1,
  magicalEffect: true, animation: "instant-death",
};

const lyra = member("Lyra", "heroes", 88);
lyra.state.template.hp_threshold_instant_death_actions = [action];
lyra.state.resources["spell-slot-9"] = 1;
const high = member("High", "monsters", 150);
const setup = { heroes: [lyra], monsters: [high] };
const P = window.IRON_PIT_BROWSER_HP_THRESHOLD_INSTANT_DEATH;

const selected = P.choose(lyra, setup);
assert.ok(selected);
const event = P.resolve(1, 1, lyra, high, action, setup);
assert.equal(event.damage_roll.total, 12);
assert.equal(high.state.current_hp, 138);
assert.equal(high.state.is_dead, false);
assert.equal(event.resource_remaining, 0);

const lyra2 = member("Lyra2", "heroes", 88);
lyra2.state.template.hp_threshold_instant_death_actions = [action];
lyra2.state.resources["spell-slot-9"] = 1;
const low = member("Low", "monsters", 100);
const setup2 = { heroes: [lyra2], monsters: [low] };
const kill = P.resolve(1, 1, lyra2, low, action, setup2);
assert.equal(kill.damage_roll, null);
assert.equal(low.state.current_hp, 0);
assert.equal(low.state.is_dead, true);

console.log("2024 Power Word Kill browser regression passed.");
