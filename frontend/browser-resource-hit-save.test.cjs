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

window.IRON_PIT_BROWSER_EXHAUSTION = {
  effectiveSpeed: (_state, speed) => speed,
};
window.IRON_PIT_BROWSER_DEBUFF_COUNTERS = {
  prevented: () => false,
};
window.IRON_PIT_DICE = {
  roll: () => 10,
};

load("browser-modifier-validation.js");
load("browser-modifiers.js");

window.IRON_PIT_BROWSER_RESOURCES = {
  available: (state, id, cost = 1) => (state.resources[id] || 0) >= cost,
  spend: (state, id, cost = 1) => {
    if ((state.resources[id] || 0) < cost) throw new Error("resource unavailable");
    state.resources[id] -= cost;
    return state.resources[id];
  },
};

let saveSucceeded = false;
window.IRON_PIT_BROWSER_SAVES = {
  resolveSavingThrow: () => ({
    roll: { notation: "1d20", rolls: [saveSucceeded ? 20 : 1], modifier: 0, total: saveSucceeded ? 20 : 1 },
    succeeded: saveSucceeded,
  }),
};

window.IRON_PIT_BROWSER_TIMED = {
  apply: (state, effectId, sourceId, options) => {
    state.active_effect_ids.push(effectId);
    state.timed_effects.push({
      effect_id: effectId,
      source_id: sourceId,
      source_effect_id: options.sourceEffectId,
      expiry_timing: options.expiryTiming,
    });
    return effectId;
  },
};

load("browser-resource-hit-save.js");

function members() {
  const rider = {
    source_id: "stunning-strike",
    source_name: "Stunning Strike",
    trigger_attack_ids: ["kael-2024-unarmed"],
    resource_id: "focus-points",
    resource_cost: 1,
    save_ability: "constitution",
    save_dc: 11,
    once_per_turn: true,
    failed_condition_id: "stunned",
    failed_condition_expiry_timing: "source_turn_start",
    successful_save_speed_multiplier: 0.5,
    successful_save_next_attack_advantage: true,
  };
  const monk = {
    combatant_id: "hero-1",
    state: {
      template: { name: "Kael Stillwater", resource_backed_on_hit_save_rider: rider },
      resources: { "focus-points": 5 },
      feature_last_turn_keys: {},
      active_modifiers: [],
      active_effect_ids: [],
      timed_effects: [],
      current_hp: 38,
      is_alive: true,
      is_dead: false,
    },
  };
  const target = {
    combatant_id: "monster-1",
    state: {
      template: { name: "Target", speed_ft: 30 },
      resources: {},
      feature_last_turn_keys: {},
      active_modifiers: [],
      active_effect_ids: [],
      timed_effects: [],
      current_hp: 20,
      is_alive: true,
      is_dead: false,
      exhaustion_level: 0,
    },
  };
  return { monk, target };
}

{
  saveSucceeded = false;
  const { monk, target } = members();
  const event = window.IRON_PIT_BROWSER_RESOURCE_HIT_SAVE.resolve(
    1, 1, monk, target, { id: "kael-2024-unarmed" }, "1:hero-1", null,
  );

  assert.equal(event.feature_id, "stunning-strike");
  assert.equal(event.save_succeeded, false);
  assert.deepEqual(event.applied_condition_ids, ["stunned"]);
  assert.equal(monk.state.resources["focus-points"], 4);
  assert.equal(target.state.timed_effects[0].expiry_timing, "source_turn_start");

  const second = window.IRON_PIT_BROWSER_RESOURCE_HIT_SAVE.resolve(
    2, 1, monk, target, { id: "kael-2024-unarmed" }, "1:hero-1", null,
  );
  assert.equal(second, null);
  assert.equal(monk.state.resources["focus-points"], 4);
}

{
  saveSucceeded = true;
  const { monk, target } = members();
  const event = window.IRON_PIT_BROWSER_RESOURCE_HIT_SAVE.resolve(
    1, 1, monk, target, { id: "kael-2024-unarmed" }, "1:hero-1", null,
  );

  assert.equal(event.save_succeeded, true);
  assert.equal(window.IRON_PIT_BROWSER_MODIFIERS.effectiveSpeed(target.state), 15);

  const advantage = target.state.active_modifiers.find(
    (item) => item.kind === "attacks-against-advantage",
  );
  const speed = target.state.active_modifiers.find(
    (item) => item.kind === "speed-multiplier",
  );
  assert.ok(advantage);
  assert.ok(speed);
  assert.equal(advantage.consume_on_attack_against, true);
  assert.equal(advantage.expires_at_start_of_source_turn, true);
  assert.equal(speed.multiplier, 0.5);
  assert.equal(speed.expires_at_start_of_source_turn, true);

  assert.equal(window.IRON_PIT_BROWSER_MODIFIERS.attacksAgainstAdvantage(target.state), 1);
  assert.equal(window.IRON_PIT_BROWSER_MODIFIERS.consumeAttacksAgainstAdvantage(target.state), 1);
  assert.equal(window.IRON_PIT_BROWSER_MODIFIERS.attacksAgainstAdvantage(target.state), 0);
}

console.log("browser resource-backed on-hit save tests passed");
