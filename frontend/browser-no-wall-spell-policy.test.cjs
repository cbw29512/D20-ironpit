"use strict";

const assert = require("node:assert/strict");
global.window = globalThis;
const registered = [];
window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION = {
  CATEGORIES: { SAVE_ZONE: "save-zone" },
  registerProvider: (value) => registered.push(value),
};
window.IRON_PIT_ACTION_ECONOMY = { available: (state) => state.action_available };
window.IRON_PIT_BROWSER_SPELLCASTING = { slotSpellAvailable: () => true };
window.IRON_PIT_BROWSER_SUPPRESSION_ZONES = { verbalBlocked: () => false };
window.IRON_PIT_BROWSER_GRID_GEOMETRY = {
  footprintDistanceFt: (a, _size, b) =>
    Math.max(Math.abs(a.x - b.x), Math.abs(a.y - b.y)) * 5,
};
require("./browser-save-zone-provider.js");

const wall = {
  id: "wall-of-fire", name: "Wall of Fire", actionCost: "action",
  damageDiceCount: 5, damageDiceSize: 8, radiusFt: 10,
  castRangeFt: 120, concentration: true, resourceId: "spell-slot-4",
};
const plague = {
  id: "insect-plague", name: "Insect Plague", actionCost: "action",
  damageDiceCount: 4, damageDiceSize: 10, radiusFt: 20,
  castRangeFt: 300, concentration: true, resourceId: "spell-slot-5",
};
const caster = {
  combatant_id: "caster", side: "heroes",
  state: {
    position: { x: 2, y: 7 }, action_available: true,
    concentration: null, resources: { "spell-slot-4": 1, "spell-slot-5": 1 },
    template: { persistent_save_zone_actions: [wall, plague] },
  },
};
const target = {
  combatant_id: "target", side: "monsters",
  state: { position: { x: 7, y: 7 }, is_alive: true, is_dead: false,
    template: { size: "medium" } },
};
const setup = {
  heroes: [caster], monsters: [target],
  map_definition: { width_squares: 24, height_squares: 16 },
  save_zones: [],
};
const selector = window.IRON_PIT_BROWSER_SAVE_ZONE_PROVIDER;
const original = JSON.stringify(caster.state.template.persistent_save_zone_actions);
assert.equal(registered.length, 1);
assert.equal(selector.chooseDamaging(caster, setup, "1:caster").action.id, "insect-plague");
caster.state.template.persistent_save_zone_actions = [wall];
assert.equal(selector.chooseDamaging(caster, setup, "1:caster"), null);
assert.equal(registered[0].discover({ member: caster, setup, turnKey: "1:caster" }), null);
assert.equal(caster.state.resources["spell-slot-4"], 1);
assert.equal(caster.state.action_available, true);
assert.deepEqual(setup.save_zones, []);
caster.state.template.persistent_save_zone_actions = [wall, plague];
assert.equal(JSON.stringify(caster.state.template.persistent_save_zone_actions), original);
console.log("Arena no-wall spell policy: browser action selection passed.");
