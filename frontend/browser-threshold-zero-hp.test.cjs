"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

load("browser-resources.js");
load("browser-zero-hp-replacement.js");
load("browser-zero-hp.js");

window.IRON_PIT_BROWSER_STATE = { effectiveMaxHp: (state) => state.template.max_hp };
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS = { endDamageSensitive: () => {} };

assert.equal(typeof window.IRON_PIT_BROWSER_ZERO_HP_REPLACEMENT.consumeDamageThreshold, "function");

function state(threshold = 7) {
  return {
    template: {
      id: "test-boar", name: "Test Boar", kind: "monster", max_hp: 20, traits: [],
      unlimited_resources: [],
      damage_threshold_zero_hp_replacements: [{
        source_id: "test-relentless", source_name: "Relentless",
        resource_id: "relentless", resource_cost: 1,
        max_trigger_damage: threshold, replacement_hp: 1,
      }],
    },
    resources: { relentless: 1 },
    current_hp: 5, max_hp_bonus: 0, temporary_hp: 0,
    is_alive: true, is_dead: false, is_unconscious: false, is_stable: false,
    death_save_successes: 0, death_save_failures: 0,
    active_effect_ids: [], active_buff_effect_ids: [], active_modifiers: [],
    pending_zero_hp_replacement_logs: [],
    concentration: null,
  };
}

{
  const target = state();
  assert.equal(window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(target, 5), "damage_threshold_zero_hp_replacement");
  assert.equal(target.current_hp, 1);
  assert.equal(target.is_dead, false);
  assert.equal(target.resources.relentless, 0);
  assert.match(window.IRON_PIT_BROWSER_ZERO_HP_REPLACEMENT.consumeLog(target), /Relentless prevents the drop to 0 HP/);

  assert.equal(window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(target, 1), "dead");
}

{
  const target = state();
  assert.equal(window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(target, 8), "dead");
  assert.equal(target.resources.relentless, 1);
}

{
  const target = state();
  assert.equal(window.IRON_PIT_BROWSER_ZERO_HP.reduceToZero(target), "dead");
  assert.equal(target.resources.relentless, 1);
}

{
  const runtime = window.IRON_PIT_BROWSER_ZERO_HP_REPLACEMENT;
  window.IRON_PIT_BROWSER_ZERO_HP_REPLACEMENT = undefined;
  assert.throws(() => window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(state(), 5), /runtime is not loaded/);
  window.IRON_PIT_BROWSER_ZERO_HP_REPLACEMENT = runtime;
}

console.log("Universal browser thresholded zero-HP replacement passed.");
