"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
global.window = globalThis;

const load = (name) => vm.runInThisContext(
  fs.readFileSync(name, "utf8"), { filename: name },
);
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "action" && state.action_available,
  spend: (state) => { state.action_available = false; },
  isIncapacitated: (state) => Boolean(state.is_unconscious),
};
load("frontend/browser-grid-geometry.js");
load("frontend/browser-grid-barriers.js");
load("frontend/browser-persistent-barriers.js");

const owner = {
  combatant_id: "owner", side: "heroes",
  state: {
    position: { x: 2, y: 7 }, action_available: true,
    resources: { "wall-of-ice": 1 }, is_dead: false, is_unconscious: false,
    template: { name: "Generic Owner", size: "medium" },
  },
};
const foe = {
  combatant_id: "foe", side: "monsters",
  state: { position: { x: 20, y: 7 }, template: { name: "Foe", size: "medium" } },
};
const setup = {
  heroes: [owner], monsters: [foe],
  map_definition: {
    width_squares: 24, height_squares: 16, cell_size_ft: 5,
    support_materials: ["stone"],
  },
  persistent_barriers: [],
};
const action = {
  id: "source-wall", name: "Generic Barrier", level: 0,
  actionCost: "action", castRangeFt: 60,
  resourceId: "wall-of-ice", resourceCost: 1,
  concentration: false, durationRounds: 10,
  permanentAfterFullDuration: false,
  endsOnSourceIncapacitated: true, endsOnSourceDeath: true,
  minSections: 3, maxSections: 3,
  sectionsMustBeContiguous: true, sectionLengthFt: 10,
  sectionHeightFt: 10, sectionThicknessInches: 12,
  armorClass: 5, hitPointsPerSection: 30,
  damageImmunities: ["cold"], damageVulnerabilities: ["fire"],
  blocksMovement: true, blocksLineOfSight: true,
};
const panels = [2, 4, 6].map((x) => ([
  { first: { x, y: 4 }, second: { x, y: 5 } },
  { first: { x: x + 1, y: 4 }, second: { x: x + 1, y: 5 } },
]));
const first = window.IRON_PIT_BROWSER_PERSISTENT_BARRIERS.cast(
  1, 1, owner, setup, action, panels, "1:owner",
);
assert.equal(first.event.resource_remaining, 0);
assert.equal(owner.state.resources["wall-of-ice"], 0);
assert.equal(setup.persistent_barriers[0].ends_on_source_incapacitated, true);
assert.equal(setup.persistent_barriers[0].ends_on_source_death, true);
owner.state.action_available = true;
assert.throws(() => window.IRON_PIT_BROWSER_PERSISTENT_BARRIERS.cast(
  2, 2, owner, setup, action, panels, "2:owner",
), /resource unavailable/);
owner.state.is_unconscious = true;
assert.equal(window.IRON_PIT_BROWSER_GRID_BARRIERS.cleanup(setup, 2).length, 1);
assert.equal(setup.persistent_barriers.length, 0);

// A different source-owned wall can expire on its source's death.
owner.state.is_unconscious = false;
owner.state.action_available = true;
owner.state.resources["wall-of-ice"] = 1;
window.IRON_PIT_BROWSER_PERSISTENT_BARRIERS.cast(
  3, 3, owner, setup, action, panels, "3:owner",
);
owner.state.is_dead = true;
assert.equal(window.IRON_PIT_BROWSER_GRID_BARRIERS.cleanup(setup, 4).length, 1);
console.log("Generic barrier resource/owner-expiry parity passed.");
