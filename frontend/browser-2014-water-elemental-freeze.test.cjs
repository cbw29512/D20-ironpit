"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

load("browser-timed-conditions.js");
load("browser-timed-control-limits.js");
load("browser-damage-taken-effects.js");
load("browser-modifiers.js");
load("browser-zero-hp.js");
load("browser-condition-lifecycle.js");

const rule = {
  sourceId: "water-elemental-freeze",
  sourceName: "Freeze",
  triggerDamageType: "cold",
  effectId: "damage-triggered-speed-penalty",
  targetTurns: 1,
  speedPenaltyFt: 20,
};

function state() {
  return {
    template: {
      id: "2014-water-elemental",
      name: "Water Elemental",
      kind: "monster",
      ruleset: "2014",
      max_hp: 100,
      speed_ft: 40,
      damage_taken_timed_effects: [rule],
    },
    current_hp: 100,
    temporary_hp: 0,
    is_alive: true,
    is_dead: false,
    active_effect_ids: [],
    timed_effects: [],
    active_modifiers: [],
    damage_taken_this_turn_by_type: {},
    turns_started: 0,
  };
}

{
  const elemental = state();
  assert.equal(window.IRON_PIT_BROWSER_MODIFIERS.effectiveSpeed(elemental), 40);

  window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(elemental, 1, false, ["fire"]);
  assert.equal(elemental.timed_effects.length, 0);
  assert.equal(window.IRON_PIT_BROWSER_MODIFIERS.effectiveSpeed(elemental), 40);

  window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(elemental, 1, false, ["cold"]);
  assert.equal(elemental.timed_effects.length, 1);
  assert.equal(window.IRON_PIT_BROWSER_MODIFIERS.effectiveSpeed(elemental), 20);

  console.log("browser freeze speed penalty tests passed");
}

{
  const another = state();
  another.template.name = "Winter Caller";
  another.template.id = "generic-winter-caller";
  another.template.damage_taken_timed_effects = [{
    ...rule, sourceId: "new-source", sourceName: "Winter Sting",
    effectId: "generic-speed-loss", speedPenaltyFt: 7,
  }];
  window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(another, 1, false, ["cold"]);
  assert.equal(window.IRON_PIT_BROWSER_MODIFIERS.effectiveSpeed(another), 33);
}
{
  const elemental = state();
  elemental.turns_started = 1;
  window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(elemental, 1, false, ["cold"]);
  assert.equal(elemental.timed_effects[0].expires_target_turn_count, 2);
  const actor = {combatant_id: "freeze-elemental", state: elemental};
  let result = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(
    1, 1, actor, "target_turn_end",
  );
  assert.equal(result.events.length, 0);
  assert.equal(window.IRON_PIT_BROWSER_MODIFIERS.effectiveSpeed(elemental), 20);
  elemental.turns_started = 2;
  result = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(
    2, 2, actor, "target_turn_end",
  );
  assert.ok(result.events.length);
  assert.equal(window.IRON_PIT_BROWSER_MODIFIERS.effectiveSpeed(elemental), 40);
}
