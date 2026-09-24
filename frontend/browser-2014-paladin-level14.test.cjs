"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

load("browser-modifiers.js");
load("browser-effect-removal.js");

window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "action" && state.action_available,
  spend: (state, cost) => { if (cost === "action") state.action_available = false; },
};
window.IRON_PIT_BROWSER_ABILITY_CHECKS = null;
window.IRON_PIT_BROWSER_SPELLCASTING = {
  slotSpellAvailable: () => true,
  markSlotSpellCast: () => { throw new Error("Cleansing Touch must not spend a spell slot."); },
};
window.IRON_PIT_BROWSER_ROLLS = {
  d20: () => { throw new Error("Cleansing Touch must not roll an ability check."); },
};
window.IRON_PIT_BROWSER_STATE = {
  distance: (a, b) => Math.abs(a.position_ft - b.position_ft),
};

const deathWard = {
  id: "death-ward", name: "Death Ward", level: 4,
  modifierEffects: [{ kind: "zero-hp-replacement", replacementHp: 1, preventsInstantDeath: true }],
};

const source = {
  combatant_id: "source-paladin", side: "heroes", position_ft: 0,
  state: {
    template: { defensive_spell_actions: [deathWard], spell_save_actions: [], spell_attack_actions: [] },
    active_modifiers: [], active_buff_effect_ids: [], resources: {}, is_alive: true, is_dead: false,
  },
};

const cleansing = {
  id: "cleansing-touch", name: "Cleansing Touch", level: 1,
  actionCost: "action", range: 5, castingAbility: "charisma",
  targetMode: "self_or_ally", autoRemoveMaxLevel: 9,
  resourceId: "cleansing-touch", resourceCost: 1,
  expendsSpellSlot: false, animation: "cleansing-touch",
};

const aurelia = {
  combatant_id: "aurelia", side: "heroes", position_ft: 0,
  state: {
    template: {
      name: "Aurelia Brightshield",
      ability_scores: { charisma: 17 },
      effect_removal_actions: [cleansing],
      defensive_spell_actions: [], spell_save_actions: [], spell_attack_actions: [],
    },
    action_available: true,
    is_alive: true, is_dead: false,
    resources: {
      "cleansing-touch": 3,
      "spell-slot-1": 4, "spell-slot-2": 3, "spell-slot-3": 3, "spell-slot-4": 1,
    },
    active_buff_effect_ids: ["death-ward"],
    active_modifiers: [{
      id: "source-paladin:death-ward:aurelia:0",
      source_id: "source-paladin",
      source_effect_id: "death-ward",
      source_name: "Death Ward",
      source_is_magical: true,
      kind: "zero-hp-replacement",
      replacement_hp: 1,
      prevents_instant_death: true,
    }],
  },
};

const setup = { heroes: [source, aurelia], monsters: [] };
const candidates = window.IRON_PIT_BROWSER_EFFECT_REMOVAL.effects(aurelia, setup, cleansing);
assert.equal(candidates.length, 1);
assert.equal(candidates[0].effectId, "death-ward");

const slotsBefore = {
  1: aurelia.state.resources["spell-slot-1"],
  2: aurelia.state.resources["spell-slot-2"],
  3: aurelia.state.resources["spell-slot-3"],
  4: aurelia.state.resources["spell-slot-4"],
};

const event = window.IRON_PIT_BROWSER_EFFECT_REMOVAL.resolve(
  1, 1, aurelia, setup, cleansing, candidates[0], "1:aurelia",
);

assert.equal(aurelia.state.action_available, false);
assert.equal(aurelia.state.resources["cleansing-touch"], 2);
assert.equal(aurelia.state.active_modifiers.length, 0);
assert.equal(aurelia.state.active_buff_effect_ids.includes("death-ward"), false);
assert.equal(event.ability_check_roll, null);
assert.equal(event.check_dc, null);
assert.equal(event.resource_remaining, 2);
assert.deepEqual({
  1: aurelia.state.resources["spell-slot-1"],
  2: aurelia.state.resources["spell-slot-2"],
  3: aurelia.state.resources["spell-slot-3"],
  4: aurelia.state.resources["spell-slot-4"],
}, slotsBefore);

console.log("2014 Paladin level 14 Cleansing Touch parity passed.");
