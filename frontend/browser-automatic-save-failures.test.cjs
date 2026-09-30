"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

let saveCalls = 0;
window.IRON_PIT_BROWSER_SAVING_THROWS = {
  resolveSavingThrow: () => {
    saveCalls += 1;
    return { roll: { total: 12 }, succeeded: true };
  },
  saveMode: () => "normal",
};
window.IRON_PIT_ACTION_ECONOMY = {
  available: () => true,
  spend: () => {},
};
window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage: (_state, amount) => amount,
  applyDamage: () => null,
};
window.IRON_PIT_BROWSER_GRAPPLE = { apply: () => [] };
window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS = {
  saveAdvantageSourceNames: () => [],
};
window.IRON_PIT_BROWSER_D20_TEST_OVERRIDE = {
  apply: (_state, roll) => ({ roll, featureId: null, sourceName: null }),
  sourceNameForRoll: () => null,
};
window.IRON_PIT_DICE = { rollMany: () => [] };

load("browser-saves.js");

function member(id, creatureType) {
  return {
    combatant_id: id,
    side: id.startsWith("actor") ? "heroes" : "monsters",
    state: {
      current_hp: 10,
      temporary_hp: 0,
      is_alive: true,
      is_dead: false,
      action_available: true,
      active_effect_ids: [],
      resources: {},
      death_save_successes: 0,
      death_save_failures: 0,
      template: {
        name: id,
        creature_type: creatureType,
        max_hp: 10,
        saving_throw_bonuses: { constitution: 0 },
        progression_features: {},
      },
    },
  };
}

const action = {
  id: "typed-save",
  name: "Typed Save",
  actionCost: "action",
  saveAbility: "constitution",
  dc: 15,
  range: 30,
  damageDiceCount: 0,
  damageDiceSize: 8,
  damageBonus: 0,
  damageType: null,
  successDamage: "none",
  automaticFailureCreatureTypes: ["Plant"],
};

const actor = member("actor:druid", "Humanoid");
const plant = member("target:plant", "Plant");
const plantEvent = window.IRON_PIT_BROWSER_SAVES.resolveAction(
  1, 1, actor, plant, action, 10,
);
assert.equal(plantEvent.save_succeeded, false);
assert.equal(plantEvent.saving_throw_roll, null);
assert.match(plantEvent.description, /automatically FAILS/);
assert.equal(saveCalls, 0);

const humanoid = member("target:humanoid", "Humanoid");
const normalEvent = window.IRON_PIT_BROWSER_SAVES.resolveAction(
  2, 1, actor, humanoid, action, 10,
);
assert.equal(normalEvent.save_succeeded, true);
assert.deepEqual(normalEvent.saving_throw_roll, { total: 12 });
assert.equal(saveCalls, 1);

console.log("Universal browser creature-type automatic save failure parity passed.");
