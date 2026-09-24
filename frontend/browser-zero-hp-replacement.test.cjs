"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

load("browser-modifiers.js");
load("browser-zero-hp-replacement.js");
load("browser-zero-hp.js");

window.IRON_PIT_BROWSER_STATE = { effectiveMaxHp: (state) => state.template.max_hp };
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS = { endDamageSensitive: () => {} };

function state() {
  return {
    template: { id: "target", name: "Target", kind: "character", max_hp: 20, traits: [], condition_immunities: [] },
    current_hp: 5, max_hp_bonus: 0, temporary_hp: 0,
    is_alive: true, is_dead: false, is_unconscious: false, is_stable: false,
    death_save_successes: 0, death_save_failures: 0,
    active_effect_ids: [], active_buff_effect_ids: ["death-ward"],
    active_modifiers: [{
      id: "caster:death-ward:target:0",
      source_id: "caster",
      source_effect_id: "death-ward",
      source_name: "Death Ward",
      source_is_magical: true,
      kind: "zero-hp-replacement",
      replacement_hp: 1,
      prevents_instant_death: true,
    }],
    pending_zero_hp_replacement_logs: [],
    concentration: null,
  };
}

{
  const target = state();
  const outcome = window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(target, 20);
  assert.equal(outcome, "zero_hp_replacement");
  assert.equal(target.current_hp, 1);
  assert.equal(target.is_dead, false);
  assert.equal(target.is_unconscious, false);
  assert.equal(target.active_modifiers.length, 0);
  assert.equal(target.active_buff_effect_ids.includes("death-ward"), false);
  assert.match(window.IRON_PIT_BROWSER_ZERO_HP_REPLACEMENT.consumeLog(target), /Death Ward prevents the drop to 0 HP/);

  const second = window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(target, 5);
  assert.equal(second, "unconscious");
  assert.equal(target.current_hp, 0);
}

{
  const target = state();
  assert.equal(window.IRON_PIT_BROWSER_ZERO_HP.reduceToZero(target), "unconscious");
  assert.equal(target.current_hp, 0);
  assert.equal(target.active_modifiers.length, 1);
  assert.equal(target.active_buff_effect_ids.includes("death-ward"), true);
}

{
  const target = state();
  assert.equal(window.IRON_PIT_BROWSER_ZERO_HP_REPLACEMENT.consumeInstantDeath(target), true);
  assert.equal(target.active_modifiers.length, 0);
  assert.match(window.IRON_PIT_BROWSER_ZERO_HP_REPLACEMENT.consumeLog(target), /Death Ward negates an instant-death effect/);
}

console.log("Universal browser zero-HP replacement passed.");
