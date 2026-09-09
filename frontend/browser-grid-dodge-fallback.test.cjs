"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
load("browser-grid-geometry.js");
load("browser-grid-movement-support.js");
load("browser-grid-path-search-support.js");
load("browser-grid-path-search.js");
load("browser-grid-movement.js");

const geometry = window.IRON_PIT_BROWSER_GRID_GEOMETRY;
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "action" ? state.action_available : state.bonus_action_available,
  spend: (state, cost) => {
    if (cost === "action") state.action_available = false;
    else if (cost === "bonus_action") state.bonus_action_available = false;
  },
};
window.IRON_PIT_BROWSER_SPELLCASTING = { slotSpellAvailable: () => true };
window.IRON_PIT_BROWSER_GRAPPLE = { speedIsZero: () => false };
window.IRON_PIT_BROWSER_REACTIONS = { resolveOpportunityAttack: () => null };
window.IRON_PIT_BROWSER_STATE = {
  distance: (a, b) => geometry.footprintDistanceFt(
    a.state.position, a.state.template.size, b.state.position, b.state.template.size,
  ),
  sizeAtMost: () => true,
};
window.IRON_PIT_BROWSER_FORMATION = {
  targetOrder: (member, setup) => member.side === "heroes" ? setup.monsters : setup.heroes,
};

load("browser-grid-reaction-support.js");
load("browser-reaction-movement.js");
load("browser-offensive-ranges.js");
load("browser-offensive-movement.js");
load("browser-dodge.js");

function member(id, side, x, y, size = "gargantuan", attacks = []) {
  try {
    return {
      combatant_id: id,
      side,
      position_ft: 0,
      state: {
        position: { x, y }, current_hp: 10, is_alive: true, is_dead: false, is_unconscious: false,
        action_available: true, bonus_action_available: true, movement_remaining_ft: 30,
        resources: {}, active_effect_ids: [], timed_effects: [], grapple_sources: [],
        template: {
          id, name: id, size, attacks, spell_attack_actions: [], spell_save_actions: [], saving_throw_actions: [],
        },
      },
    };
  } catch (error) {
    console.error("Failed browser Gargantuan fallback fixture", { id, error });
    throw error;
  }
}

const melee = [{ id: "club", name: "Club", kind: "melee", reach: 5 }];
const mover = member("hero-mover", "heroes", 0, 6, "gargantuan", melee);
const wall = [
  member("hero-wall-1", "heroes", 4, 0),
  member("hero-wall-2", "heroes", 4, 4),
  member("hero-wall-3", "heroes", 4, 8),
  member("hero-wall-4", "heroes", 4, 12),
];
const target = member("monster-target", "monsters", 20, 7, "medium");
const setup = {
  heroes: [mover, ...wall], monsters: [target],
  map_definition: { id: "iron-pit-standard", width_squares: 24, height_squares: 16, cell_size_ft: 5 },
};

const movement = window.IRON_PIT_BROWSER_OFFENSIVE_MOVEMENT.move(1, 1, mover, setup, "1:hero-mover");
assert.deepEqual(movement.events, []);
assert.deepEqual(mover.state.position, { x: 0, y: 6 });
assert.equal(mover.state.action_available, true);

const dodge = window.IRON_PIT_BROWSER_DODGE.take(1, 1, mover);
assert.equal(dodge.feature_id, "dodge");
assert.equal(mover.state.active_effect_ids.includes("dodge"), true);
assert.equal(mover.state.action_available, false);

console.log("Blocked Gargantuan browser Dodge fallback regression passed.");
