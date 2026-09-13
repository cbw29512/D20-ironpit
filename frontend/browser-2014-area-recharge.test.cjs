"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

window.IRON_PIT_BROWSER_CONDITION_RULES = {
  incapacitated: () => false,
  autoFailStrDex: () => false,
};
window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage: (_state, amount) => amount,
  applyDamage: (state, amount) => {
    state.current_hp -= amount;
    if (state.current_hp <= 0) {
      state.current_hp = 0;
      state.is_alive = false;
      state.is_dead = true;
    }
    return null;
  },
};
window.IRON_PIT_BROWSER_GRAPPLE = { apply: () => [] };
window.IRON_PIT_BROWSER_BARBARIAN2 = { dangerSenseAdvantage: () => 0 };
window.IRON_PIT_BROWSER_DODGE = { dexSaveAdvantageSources: () => 0 };
window.IRON_PIT_BROWSER_MODIFIERS = { applyD20Bonus: (_state, _kind, roll) => roll };
window.IRON_PIT_BROWSER_CONCENTRATION = { endIfIncapacitated: () => {} };
window.IRON_PIT_BROWSER_STATE = {
  sizeAtMost: () => true,
  distance: (a, b) => Math.hypot(a.state.position.x - b.state.position.x, a.state.position.y - b.state.position.y) * 5,
};

load("browser-source-effect-immunity.js");
load("browser-save-control-effects.js");
load("browser-action-economy.js");
load("browser-rolls.js");
load("browser-saves.js");
load("browser-death-triggers.js");
load("browser-grid-geometry.js");
load("browser-area-shapes.js");
load("browser-area-targeting.js");
load("browser-area-save-actions.js");

function dice(values) {
  const queue = [...values];
  window.IRON_PIT_DICE = {
    roll: () => {
      if (!queue.length) throw new Error("unexpected die roll");
      return queue.shift();
    },
    rollMany: (count) => Array.from({ length: count }, () => {
      if (!queue.length) throw new Error("unexpected die roll");
      return queue.shift();
    }),
  };
}

function member(id, side, x, y) {
  return {
    combatant_id: id,
    side,
    position_ft: x * 5,
    state: {
      position: { x, y },
      action_available: true,
      bonus_action_available: true,
      reaction_available: true,
      turn_terminated: false,
      is_alive: true,
      is_dead: false,
      is_unconscious: false,
      is_stable: false,
      current_hp: 50,
      temporary_hp: 0,
      death_save_successes: 0,
      death_save_failures: 0,
      active_effect_ids: [],
      grapple_sources: [],
      resources: {},
      source_effect_immunities: [],
      concentration: null,
      feature_last_turn_keys: {},
      template: {
        name: id,
        size: "medium",
        traits: [],
        saving_throw_bonuses: { dexterity: 0 },
        resource_definitions: [],
        saving_throw_actions: [],
        death_trigger_actions: [],
      },
    },
  };
}

const actor = member("monster-1:breather", "monsters", 1, 1);
const first = member("hero-1:first", "heroes", 2, 1);
const second = member("hero-2:second", "heroes", 3, 1);
const action = {
  id: "fire-breath",
  name: "Fire Breath",
  saveAbility: "dexterity",
  dc: 20,
  range: 30,
  area: { shape: "line", origin: "self", lengthFt: 30, widthFt: 5 },
  damageDiceCount: 2,
  damageDiceSize: 6,
  damageBonus: 0,
  damageType: "fire",
  successDamage: "half",
  resourceId: "fire-breath",
  resourceCost: 1,
};
actor.state.template.saving_throw_actions = [action];
actor.state.template.resource_definitions = [{
  id: "fire-breath",
  name: "Fire Breath",
  maxUses: 1,
  recharge: { trigger: "start_of_turn", dieSize: 6, minimumRoll: 5 },
}];
actor.state.resources["fire-breath"] = 1;
const setup = {
  heroes: [first, second],
  monsters: [actor],
  map_definition: { id: "test", width_squares: 10, height_squares: 10, cell_size_ft: 5 },
};

dice([3, 4, 1, 20]);
const resolved = window.IRON_PIT_BROWSER_AREA_SAVES.resolve(1, 1, actor, setup, true);
assert.ok(resolved);
assert.equal(resolved.events.length, 2);
assert.equal(actor.state.resources["fire-breath"], 0);
assert.deepEqual(resolved.events[0].damage_components[0].rolls, [3, 4]);
assert.deepEqual(resolved.events[1].damage_components[0].rolls, [3, 4]);
assert.equal(resolved.events[0].resource_remaining, 0);
assert.equal(resolved.events[1].resource_remaining, 0);
assert.equal(actor.state.action_available, false);

const burst = {
  id: "death-burst", name: "Death Burst", saveAbility: "dexterity", dc: 20, range: 5,
  damageDiceCount: 1, damageDiceSize: 6, damageBonus: 0, damageType: "fire",
  successDamage: "none", animation: "death-burst",
};
const firstBurst = member("monster-2:first-burst", "monsters", 1, 4);
const secondBurst = member("monster-3:second-burst", "monsters", 2, 4);
const burstTarget = member("hero-3:burst-target", "heroes", 3, 4);
firstBurst.state.current_hp = 0; firstBurst.state.is_alive = false; firstBurst.state.is_dead = true;
firstBurst.state.template.death_trigger_actions = [burst];
secondBurst.state.current_hp = 3; secondBurst.state.template.death_trigger_actions = [burst];
burstTarget.state.current_hp = 10;
const burstSetup = { heroes: [burstTarget], monsters: [firstBurst, secondBurst] };
dice([4, 1, 5, 1]);
const chained = window.IRON_PIT_BROWSER_DEATH_TRIGGERS.resolvePending(20, 2, burstSetup);
assert.equal(chained.events.length, 2);
assert.equal(secondBurst.state.is_dead, true);
assert.equal(burstTarget.state.current_hp, 5);
assert.equal(firstBurst.state.feature_last_turn_keys["death-trigger:death-burst"], "fired");
assert.equal(secondBurst.state.feature_last_turn_keys["death-trigger:death-burst"], "fired");

const shapes = window.IRON_PIT_BROWSER_AREA_SHAPES;
assert.equal(shapes.coneContains([0, 0], [1, 0], [10, 0], 15), true);
assert.equal(shapes.coneContains([0, 0], [1, 0], [10, 10], 15), false);

console.log("2014 browser Recharge AoE and Death Burst regressions passed.");
