"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

load("browser-rolls.js");
load("browser-timed-conditions.js");
load("browser-timed-control-limits.js");
load("browser-damage-taken-effects.js");
load("browser-ability-checks.js");
load("browser-zero-hp.js");
load("browser-condition-lifecycle.js");

const rule = {
  sourceId: "yeti-fear-of-fire",
  sourceName: "Fear of Fire",
  triggerDamageType: "fire",
  effectId: "damage-triggered-disadvantage",
  targetTurns: 1,
  attackRollDisadvantage: true,
  abilityCheckDisadvantage: true,
};

function state() {
  return {
    template: {
      id: "2014-yeti",
      name: "Yeti",
      kind: "monster",
      ruleset: "2014",
      max_hp: 100,
      damage_taken_timed_effects: [rule],
    },
    current_hp: 100,
    temporary_hp: 0,
    is_alive: true,
    is_dead: false,
    is_unconscious: false,
    is_stable: false,
    active_effect_ids: [],
    timed_effects: [],
    active_modifiers: [],
    damage_types_taken_since_regen: [],
    damage_taken_this_turn_by_type: {},
    turns_started: 0,
    death_save_successes: 0,
    death_save_failures: 0,
  };
}

{
  const yeti = state();
  window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(yeti, 1, false, ["cold"]);
  assert.equal(yeti.timed_effects.length, 0);

  window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(yeti, 1, false, ["fire"]);
  assert.equal(yeti.timed_effects.length, 1);
  assert.equal(window.IRON_PIT_BROWSER_TIMED_CONTROL.attackRollDisadvantage(yeti), 1);
  assert.equal(window.IRON_PIT_BROWSER_TIMED_CONTROL.abilityCheckDisadvantage(yeti), 1);
  assert.equal(window.IRON_PIT_BROWSER_TIMED_CONTROL.abilityD20Disadvantage(yeti, "strength"), 0);
  assert.equal(window.IRON_PIT_BROWSER_ABILITY_CHECKS.mode(yeti), "disadvantage");
}

{
  const yeti = state();
  window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(yeti, 1, false, ["fire"]);
  assert.equal(yeti.timed_effects[0].expires_target_turn_count, 1);
  yeti.turns_started = 1;
  const member = { combatant_id: "yeti-before", state: yeti };
  const result = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(
    1, 1, member, "target_turn_end",
  );
  assert.ok(result.events.length > 0);
  assert.equal(yeti.timed_effects.length, 0);
}

{
  const yeti = state();
  yeti.turns_started = 1;
  window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(yeti, 1, false, ["fire"]);
  assert.equal(yeti.timed_effects[0].expires_target_turn_count, 2);
  const member = { combatant_id: "yeti-during", state: yeti };

  let result = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(
    1, 1, member, "target_turn_end",
  );
  assert.equal(result.events.length, 0);
  assert.equal(yeti.timed_effects.length, 1);

  yeti.turns_started = 2;
  result = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(
    1, 2, member, "target_turn_end",
  );
  assert.ok(result.events.length > 0);
  assert.equal(yeti.timed_effects.length, 0);
}

console.log("2014 Fear of Fire browser runtime passed.");
