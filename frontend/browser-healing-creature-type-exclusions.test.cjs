"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = globalThis;
window.IRON_PIT_ACTION_ECONOMY = {
  available: () => true,
  spend: () => {},
};
window.IRON_PIT_BROWSER_SPELLCASTING = {
  slotSpellAvailable: () => true,
  markSlotSpellCast: () => {},
};
window.IRON_PIT_BROWSER_STATE = {
  effectiveMaxHp: (state) => state.template.max_hp,
};

const load = (name) => vm.runInThisContext(
  fs.readFileSync(`frontend/${name}`, "utf8"),
  { filename: name },
);
load("browser-healing-policy.js");
load("browser-healing.js");
load("browser-group-healing.js");

const H = window.IRON_PIT_BROWSER_HEALING;

function member(id, creatureType, hp) {
  return {
    combatant_id: id,
    side: "heroes",
    position_ft: 0,
    state: {
      template: {
        id,
        name: id,
        max_hp: 20,
        creature_type: creatureType,
        traits: [],
      },
      current_hp: hp,
      is_alive: true,
      is_dead: false,
      death_save_failures: 0,
    },
  };
}

const healer = member("healer", "Humanoid", 20);
const undead = member("undead", "Undead", 1);
const construct = member("construct", "Construct", 1);
const shapedUndead = member("shaped-undead", "Undead (shapechanger)", 1);
const humanoid = member("humanoid", "Humanoid", 1);
const action = {
  id: "typed-heal",
  name: "Typed Heal",
  actionCost: "action",
  range: 60,
  targetMode: "self_or_ally",
  maxTargets: 6,
  healingBonus: 3,
  excludedCreatureTypes: ["undead", "construct"],
};

for (const target of [undead, construct, shapedUndead]) {
  assert.equal(
    H.chooseTarget(healer, { heroes: [healer, target], monsters: [] }, action),
    null,
  );
}
assert.equal(
  H.chooseTarget(healer, { heroes: [healer, humanoid], monsters: [] }, action),
  humanoid,
);
assert.deepEqual(
  H.groupTargets(
    healer,
    { heroes: [healer, undead, construct, humanoid], monsters: [] },
    action,
  ).map((item) => item.combatant_id),
  ["humanoid"],
);

console.log("Browser healing creature-type exclusion regressions passed.");
