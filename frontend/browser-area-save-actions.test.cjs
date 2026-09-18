"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

window.IRON_PIT_BROWSER_GRID_GEOMETRY = {
  occupiedCells: (position) => [[position.x, position.y]],
};
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state) => state.action_available,
  spend: (state) => { state.action_available = false; },
};
const calls = [];
window.IRON_PIT_BROWSER_SAVES = {
  legalAction: () => true,
  resolveAction: (sequence, round, actor, target, action, distance, options) => {
    calls.push({ target: target.combatant_id, rolls: [...options.sharedDamageRolls] });
    return {
      sequence, round_number: round, event_type: "saving_throw",
      actor_id: actor.combatant_id, target_id: target.combatant_id,
      resource_remaining: options.resourceRemaining,
      damage_components: [{ rolls: [...options.sharedDamageRolls] }],
    };
  },
};
window.IRON_PIT_DICE = { rollMany: () => [1, 2] };

load("browser-area-shapes.js");
load("browser-area-targeting.js");
load("browser-area-save-actions.js");

function member(id, side, x, y) {
  return {
    combatant_id: id, side, position_ft: x * 5,
    state: {
      position: { x, y }, is_alive: true, is_dead: false, current_hp: 10,
      action_available: true, resources: {},
      grapple_sources: [], template: { size: "medium", saving_throw_actions: [] },
    },
  };
}

const actor = member("monster:breather", "monsters", 1, 1);
const first = member("hero:first", "heroes", 2, 1);
const second = member("hero:second", "heroes", 3, 1);
const action = {
  id: "fire-breath", name: "Fire Breath", saveAbility: "dexterity", dc: 12,
  range: 15, area: { shape: "cone", origin: "self", length_ft: 15 },
  damageDiceCount: 2, damageDiceSize: 6, damageType: "fire",
  successDamage: "half", resourceId: "fire-breath", resourceCost: 1,
};
actor.state.template.saving_throw_actions = [action];
actor.state.resources["fire-breath"] = 1;
const setup = {
  heroes: [first, second], monsters: [actor],
  map_definition: { width_squares: 10, height_squares: 10 },
};

const A = window.IRON_PIT_BROWSER_AREA_SAVES;
const selected = A.choose(actor, setup);
assert.ok(selected);
assert.equal(selected.action.id, "fire-breath");
assert.deepEqual(new Set(selected.placement.targetIds), new Set(["hero:first", "hero:second"]));

const result = A.resolve(1, 1, actor, setup, selected);
assert.equal(result.sequence, 3);
assert.equal(result.events.length, 2);
assert.equal(actor.state.resources["fire-breath"], 0);
assert.equal(actor.state.action_available, false);
assert.deepEqual(calls, [
  { target: "hero:first", rolls: [1, 2] },
  { target: "hero:second", rolls: [1, 2] },
]);
assert.ok(result.events.every((event) => event.resource_remaining === 0));

console.log("Universal browser area-save resource parity passed.");
