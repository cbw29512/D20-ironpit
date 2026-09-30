"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = globalThis;
const load = (path) => vm.runInThisContext(fs.readFileSync(path, "utf8"), { filename: path });

window.IRON_PIT_BROWSER_SAVING_THROWS = {
  resolveSavingThrow: () => ({ roll: 1, succeeded: false }),
  saveMode: () => "normal",
};
window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS = {
  saveAdvantageSourceNames: () => [],
};
window.IRON_PIT_BROWSER_D20_TEST_OVERRIDE = {
  sourceNameForRoll: () => null,
};
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "action" && state.action_available,
  spend: (state) => { state.action_available = false; },
};

load("frontend/browser-grid-geometry.js");
load("frontend/browser-grid-barriers.js");
load("frontend/browser-forced-movement.js");
load("frontend/browser-saves.js");

function member(id, side, x, y) {
  return {
    combatant_id: id,
    side,
    state: {
      position: { x, y },
      action_available: true,
      resources: {},
      active_effect_ids: [],
      current_hp: 20,
      max_hp: 20,
      temporary_hp: 0,
      death_save_successes: 0,
      death_save_failures: 0,
      is_alive: true,
      is_dead: false,
      is_unconscious: false,
      is_stable: false,
      concentration: null,
      template: {
        id,
        name: id,
        size: "medium",
        creature_type: "Humanoid",
        progression_features: { evasion: false },
      },
    },
  };
}

const actor = member("actor", "heroes", 1, 1);
const target = member("target", "monsters", 2, 1);
const setup = {
  heroes: [actor],
  monsters: [target],
  map_definition: { width_squares: 8, height_squares: 8, cell_size_ft: 5 },
  persistent_barriers: [],
};
const action = {
  id: "test-wave",
  name: "Test Wave",
  actionCost: "action",
  saveAbility: "constitution",
  dc: 40,
  range: 15,
  failedSavePushFt: 10,
  magicalEffect: true,
  successDamage: "none",
};

const event = window.IRON_PIT_BROWSER_SAVES.resolveAction(
  1, 1, actor, target, action, 5, { setup },
);
assert.equal(event.save_succeeded, false);
assert.deepEqual(target.state.position, { x: 4, y: 1 });
assert.match(event.description, /pushed 10 feet away/);

console.log("browser failed-save forced movement tests passed");
