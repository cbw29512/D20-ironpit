"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

window.IRON_PIT_ACTION_ECONOMY = { available: () => true };
window.IRON_PIT_BROWSER_SPELLCASTING = { slotSpellAvailable: () => false };
window.IRON_PIT_BROWSER_RESOURCES = { available: () => true };
window.IRON_PIT_BROWSER_STATE = {
  distance: () => 25,
  sizeAtMost: () => true,
};
window.IRON_PIT_BROWSER_FORMATION = { targetOrder: () => [target] };
window.IRON_PIT_BROWSER_GRID_MOVEMENT = {
  planToward: (_map, _member, _target, _members, desiredDistance) => ({
    goal_reachable: true,
    path: desiredDistance === 15 ? [{ x: 2, y: 0 }, { x: 3, y: 0 }] : [],
    movement_cost_ft: desiredDistance === 15 ? 10 : 0,
    final_distance_ft: desiredDistance === 15 ? 15 : 25,
  }),
};
window.IRON_PIT_BROWSER_REACTION_MOVEMENT = {};

const member = {
  combatant_id: "actor",
  side: "monsters",
  state: {
    position: { x: 1, y: 0 },
    movement_remaining_ft: 30,
    template: {
      attacks: [{ id: "fallback-bow", kind: "ranged", long: 80 }],
      saving_throw_actions: [{
        id: "recharge-cone",
        range: 0,
        area: { shape: "cone", origin: "self", lengthFt: 15 },
        resourceId: "breath-use",
        resourceCost: 1,
      }],
      spell_attack_actions: [],
      spell_save_actions: [],
      resourceDefinitions: {
        "breath-use": { id: "breath-use", maxUses: 1, recharge: { minimumRoll: 5 } },
      },
    },
  },
};
const target = {
  combatant_id: "target",
  side: "heroes",
  state: { position: { x: 6, y: 0 }, grapple_sources: [], template: {} },
};
const setup = { heroes: [target], monsters: [member], map_definition: { id: "test" } };

load("browser-offensive-ranges.js");
load("browser-offensive-movement.js");

const ranges = window.IRON_PIT_BROWSER_OFFENSIVE_RANGES.rangesForTarget(member, target, "1:actor");
assert.ok(ranges.some((option) => option.family === "ranged" && option.range === 80 && option.priority === 1));
assert.ok(ranges.some((option) => option.family === "ability" && option.range === 15 && option.priority === 0));

const intent = window.IRON_PIT_BROWSER_OFFENSIVE_MOVEMENT.chooseIntent(member, setup, "1:actor");
assert.ok(intent);
assert.equal(intent.targetId, "target");
assert.equal(intent.family, "ability");
assert.equal(intent.desiredDistanceFt, 15);
console.log("Browser movement prefers reachable Recharge AoE over a legal ranged fallback.");