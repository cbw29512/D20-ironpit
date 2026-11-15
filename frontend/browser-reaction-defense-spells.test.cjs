"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), {filename: name},
);
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "reaction" && state.reaction_available && !state.is_dead,
  spend: (state) => {state.reaction_available = false;},
};
window.IRON_PIT_BROWSER_MODIFIERS = {
  effectiveArmorClass: (state) => state.template.armor_class +
    (state.active_modifiers || []).filter((item) => item.kind === "armor-class")
      .reduce((total, item) => total + item.flat_bonus, 0),
  add: (state, modifier) => state.active_modifiers.push(modifier),
  expireSourceTurnStart: (states, sourceId) => {
    for (const state of states) state.active_modifiers = state.active_modifiers.filter(
      (item) => !(item.expires_at_start_of_source_turn && item.source_id === sourceId),
    );
  },
};
load("browser-reaction-defense-spells.js");
const D = window.IRON_PIT_BROWSER_REACTION_DEFENSE_SPELLS;
const state = () => ({
  reaction_available: true, is_dead: false, active_modifiers: [],
  resources: {"spell-slot-1": 1},
  template: {
    id: "mage", name: "Mage", armor_class: 12,
    reaction_defense_spell: {
      id: "shield", name: "Shield", minimumSlotLevel: 1,
      acBonus: 5, blockedAutoHitSpellIds: ["magic-missile"],
    },
  },
});
{
  const s = state();
  assert.equal(D.trigger(s, "mage-1", {attackTotal: 15, natural: 12}), true);
  assert.equal(window.IRON_PIT_BROWSER_MODIFIERS.effectiveArmorClass(s), 17);
  assert.equal(s.reaction_available, false);
  assert.equal(s.resources["spell-slot-1"], 0);
  assert.equal(D.blocksAutoHit(s, "mage-1", "magic-missile"), true);
  window.IRON_PIT_BROWSER_MODIFIERS.expireSourceTurnStart([s], "mage-1");
  assert.equal(D.active(s), false);
}
for (const options of [
  {attackTotal: 11, natural: 12}, {attackTotal: 17, natural: 12},
  {attackTotal: 15, natural: 20},
]) {
  const s = state();
  assert.equal(D.trigger(s, "mage-1", options), false);
  assert.equal(s.reaction_available, true);
  assert.equal(s.resources["spell-slot-1"], 1);
}
{
  const s = state();
  assert.equal(D.blocksAutoHit(s, "mage-1", "different-spell"), false);
  assert.equal(D.blocksAutoHit(s, "mage-1", "magic-missile"), true);
  assert.equal(s.resources["spell-slot-1"], 0);
}
{
  const s = state();
  s.resources["spell-slot-1"] = 0;
  assert.equal(D.trigger(s, "mage-1", {attackTotal: 15, natural: 10}), false);
  assert.equal(D.blocksAutoHit(s, "mage-1", "magic-missile"), false);
}
console.log("Universal Shield reaction browser parity passed");
