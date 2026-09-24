"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

let spent = 0;
let rolled = false;
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "action" && state.action_available,
  spend: (state) => { state.action_available = false; spent += 1; },
};
window.IRON_PIT_BROWSER_ABILITY_CHECKS = {
  resolve: () => { throw new Error("Cleansing Touch must not roll an ability check."); },
};
window.IRON_PIT_BROWSER_MODIFIERS = {
  removeSource: (states, sourceId, effectId) => {
    for (const state of states) {
      state.active_modifiers = state.active_modifiers.filter((item) =>
        !(item.source_id === sourceId && item.source_effect_id === effectId));
    }
  },
};
window.IRON_PIT_BROWSER_SPELLCASTING = {
  slotSpellAvailable: () => true,
  markSlotSpellCast: () => { throw new Error("Cleansing Touch must not expend a spell slot."); },
};
window.IRON_PIT_BROWSER_ROLLS = {
  d20: () => { rolled = true; throw new Error("Cleansing Touch must not roll."); },
};
window.IRON_PIT_BROWSER_STATE = {
  distance: (a, b) => Math.abs(a.position_ft - b.position_ft),
};

load("browser-effect-removal.js");

function member(id, side, position, template) {
  return {
    combatant_id: id,
    side,
    position_ft: position,
    state: {
      template,
      is_alive: true,
      is_dead: false,
      action_available: true,
      resources: { "cleansing-touch": 3, "spell-slot-3": 3 },
      active_modifiers: [],
      active_buff_effect_ids: [],
    },
  };
}

const sanctuarySpell = {
  id: "sanctuary", name: "Sanctuary", level: 1,
};

const source = member("source", "heroes", 5, {
  name: "Source",
  defensive_spell_actions: [sanctuarySpell],
  spell_save_actions: [],
  spell_attack_actions: [],
  ability_scores: { charisma: 10 },
});
source.state.active_modifiers.push({
  id: "source:sanctuary:source:0",
  source_id: "source",
  source_effect_id: "sanctuary",
  kind: "targeting-save-gate",
});
source.state.active_buff_effect_ids.push("sanctuary");

const remover = member("aurelia", "heroes", 0, {
  name: "Aurelia Brightshield",
  ability_scores: { charisma: 17 },
  defensive_spell_actions: [],
  spell_save_actions: [],
  spell_attack_actions: [],
  effect_removal_actions: [
    {
      id: "cleansing-touch", name: "Cleansing Touch", level: 0,
      actionCost: "action", range: 5, castingAbility: "charisma",
      targetMode: "self_or_ally", autoRemoveMaxLevel: 9,
      resourceId: "cleansing-touch", resourceCost: 1,
      expendsSpellSlot: false, animation: "cleansing-touch",
    },
    {
      id: "dispel-magic", name: "Dispel Magic", level: 3,
      actionCost: "action", range: 120, castingAbility: "charisma",
      targetMode: "enemy", autoRemoveMaxLevel: 3,
      resourceId: "spell-slot-3", resourceCost: 1,
      expendsSpellSlot: true, animation: "dispel-magic",
    },
  ],
});

const setup = { heroes: [remover, source], monsters: [] };
const turnKey = "1:aurelia";
const choice = window.IRON_PIT_BROWSER_EFFECT_REMOVAL.choose(remover, setup, turnKey);

assert.ok(choice);
assert.equal(choice.action.id, "cleansing-touch");
const beforeSlot = remover.state.resources["spell-slot-3"];
const event = window.IRON_PIT_BROWSER_EFFECT_REMOVAL.resolve(
  1, 1, remover, setup, choice.action, choice.effect, turnKey,
);

assert.equal(spent, 1);
assert.equal(rolled, false);
assert.equal(remover.state.resources["cleansing-touch"], 2);
assert.equal(remover.state.resources["spell-slot-3"], beforeSlot);
assert.equal(event.ability_check_roll, null);
assert.equal(event.check_dc, null);
assert.deepEqual(event.removed_condition_ids, ["sanctuary"]);
assert.equal(source.state.active_modifiers.length, 0);
assert.equal(source.state.active_buff_effect_ids.includes("sanctuary"), false);

console.log("2014 Paladin level 14 Cleansing Touch parity passed.");
