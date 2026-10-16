"use strict";
const assert = require("node:assert/strict");
global.window = globalThis;
const providers = new Map();
window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION = {
  CATEGORIES: {
    SPELL_OFFENSE: "spell", INTIMIDATING_PRESENCE_2014: "presence",
    AREA_WEAPON_ATTACK: "area-weapon", ATTACK_ACTION: "attack",
    AREA_SAVE: "area-save", SAVE_ACTION: "save",
    STANDARD_ATTACK: "standard", DODGE: "dodge",
  },
  registerProvider: (provider) => providers.set(provider.id, provider),
};
window.IRON_PIT_ACTION_ECONOMY = { available: () => true };
window.IRON_PIT_BROWSER_FORMATION = {
  targetOrder: (_actor, setup) => setup.monsters,
  saveDistance: () => 5,
};
window.IRON_PIT_BROWSER_RESOURCES = { available: () => true };
window.IRON_PIT_BROWSER_SAVES = { legalAction: () => true };
window.IRON_PIT_BROWSER_MULTI_SAVE_PROVIDER = { choose: () => null };
window.IRON_PIT_BROWSER_AREA_SAVES = {
  choose: (actor) => {
    const action = actor.state.template.saving_throw_actions.find((item) => item.area);
    return action ? { action, placement: { targetIds: ["target"] } } : null;
  },
};
require("./browser-main-action-providers.js");
const target = { combatant_id: "target" };
const setup = { monsters: [target], heroes: [] };
const actor = { combatant_id: "synthetic", state: { template: { saving_throw_actions: [] } } };
const parts = [
  { diceCount: 3, diceSize: 6, damageBonus: 4, damageType: "bludgeoning" },
  { diceCount: 3, diceSize: 6, damageBonus: 4, damageType: "slashing" },
];
for (const name of ["Synthetic Leap", "Renamed Homebrew"]) {
  const action = { id: "source-save", name, range: 15, damageComponents: parts };
  actor.state.template.saving_throw_actions = [action];
  assert.equal(providers.get("save-action").discover({ member: actor, setup }).payload.expectedDamage, 29);
  actor.state.template.saving_throw_actions = [{ ...action, area: { shape: "cone" } }];
  assert.equal(providers.get("area-save").discover({ member: actor, setup }).payload.expectedDamage, 29);
}
console.log("Typed save Action scoring parity passed.");
