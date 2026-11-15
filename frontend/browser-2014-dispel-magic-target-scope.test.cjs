"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
window.IRON_PIT_BROWSER_STATE = {
  distance: (a, b) => Math.abs(a.position_ft - b.position_ft),
};
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-effect-removal.js"), "utf8"),
  {filename: "browser-effect-removal.js"},
);
const api = window.IRON_PIT_BROWSER_EFFECT_REMOVAL;
const action = {id: "dispel-magic", name: "Dispel Magic", targetMode: "any", range: 120};
const spell = (id, level) => ({id, level});
function member(id, side, position, spells = [], buffs = []) {
  return {
    combatant_id: id, side, position_ft: position,
    state: {
      is_alive: true, is_dead: false,
      template: {
        defensive_spell_actions: spells,
        spell_save_actions: [], spell_attack_actions: [],
        effect_tag_condition_grants: [],
      },
      active_modifiers: buffs,
    },
  };
}
try {
  const actor = member("actor", "heroes", 0, [spell("bless", 1)]);
  const friend = member("friend", "heroes", 5, [], [
    {source_id: "actor", source_effect_id: "bless"},
  ]);
  const hostile = member("hostile", "monsters", 40, [spell("haste", 3)]);
  const foe = member("foe", "monsters", 30, [], [
    {source_id: "hostile", source_effect_id: "haste"},
  ]);
  const setup = {heroes: [actor, friend], monsters: [hostile, foe]};
  const found = api.effects(actor, setup, action);
  assert.deepEqual(found.map((x) => [x.effectId, x.target.combatant_id]), [
    ["haste", "foe"], ["bless", "friend"],
  ]);
  const friendlyOnly = api.effects(actor, {heroes: [actor, friend], monsters: []}, action);
  assert.equal(friendlyOnly.length, 1);
  assert.equal(friendlyOnly[0].target.combatant_id, "friend");
  foe.position_ft = 121;
  assert.deepEqual(api.effects(actor, setup, action).map((x) => x.effectId), ["bless"]);
  console.log("Dispel Magic 2014 any-side target parity and hostile-first selection passed");
} catch (error) {
  console.error("Dispel Magic 2014 target parity failed", error);
  process.exitCode = 1;
}
