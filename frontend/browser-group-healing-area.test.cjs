"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = globalThis;
window.IRON_PIT_ACTION_ECONOMY = {
  available: () => true,
  spend: (state) => { state.action_available = false; },
};
window.IRON_PIT_BROWSER_SPELLCASTING = {
  slotSpellAvailable: () => true,
  markSlotSpellCast: () => {},
};
window.IRON_PIT_BROWSER_STATE = {
  effectiveMaxHp: (state) => state.template.max_hp,
};
window.IRON_PIT_DICE = { roll: () => 8 };

const load = (name) => vm.runInThisContext(
  fs.readFileSync(`frontend/${name}`, "utf8"),
  { filename: name },
);
load("browser-spell-area.js");
load("browser-healing-policy.js");
load("browser-healing.js");
load("browser-group-healing.js");

function member(id, position, hp) {
  return {
    combatant_id: id,
    side: "heroes",
    position_ft: position,
    state: {
      template: {
        id,
        name: id,
        max_hp: 20,
        creature_type: "Humanoid",
        traits: [],
      },
      resources: {},
      current_hp: hp,
      is_alive: true,
      is_dead: false,
      is_unconscious: false,
      is_stable: false,
      death_save_successes: 0,
      death_save_failures: 0,
      action_available: true,
    },
  };
}

const healer = member("healer", 0, 20);
healer.state.resources["spell-slot-5"] = 1;
const reachable = member("reachable", 80, 1);
const tooFar = member("too-far", 95, 1);
const setup = { heroes: [healer, reachable, tooFar], monsters: [] };
const action = {
  id: "area-heal",
  name: "Area Heal",
  actionCost: "action",
  range: 60,
  areaRadiusFt: 30,
  targetMode: "self_or_ally",
  maxTargets: 6,
  diceCount: 1,
  diceSize: 8,
  healingBonus: 0,
  resourceId: "spell-slot-5",
  resourceCost: 1,
  excludedCreatureTypes: [],
};

const targets = window.IRON_PIT_BROWSER_HEALING.groupTargets(
  healer, setup, action, "1:healer",
);
assert.deepEqual(targets.map((item) => item.combatant_id), ["reachable"]);

const result = window.IRON_PIT_BROWSER_HEALING.resolveGroup(
  1, 1, healer, [reachable], action, "1:healer", setup,
);
assert.equal(result.events.length, 1);
assert.equal(result.events[0].target_id, "reachable");
assert.equal(healer.state.resources["spell-slot-5"], 0);

healer.state.resources["spell-slot-5"] = 1;
healer.state.action_available = true;
assert.throws(
  () => window.IRON_PIT_BROWSER_HEALING.resolveGroup(
    2, 1, healer, [tooFar], action, "2:healer", setup,
  ),
  /legal healing area/,
);

console.log("Browser area group-healing regressions passed.");
