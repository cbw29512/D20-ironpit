"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), {filename: name},
);
window.IRON_PIT_BROWSER_STATE = {
  distance: (a, b) => Math.abs(a.position_ft - b.position_ft),
};
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state) => state.action_available,
  spend: (state) => {state.action_available = false;},
};
window.IRON_PIT_BROWSER_SPELLCASTING = {
  slotSpellAvailable: (state, turnKey) => state.spell_slot_expended_turn_key !== turnKey,
  markSlotSpellCast: (state, turnKey) => {state.spell_slot_expended_turn_key = turnKey;},
};
window.IRON_PIT_BROWSER_MODIFIERS = {
  removeSource: (states, owner, effect) => {
    for (const state of states) {
      state.active_modifiers = state.active_modifiers.filter(
        (item) => item.source_id !== owner || item.source_effect_id !== effect,
      );
    }
  },
};
window.IRON_PIT_BROWSER_ROLLS = {
  d20: () => ({notation: "1d20", rolls: [1], selected_roll: 1, modifier: 0, total: 1}),
};
window.IRON_PIT_BROWSER_ABILITY_CHECKS = {
  mode: () => "normal", resolve: (_state, _ability, roll, dc) =>
    ({roll, succeeded: roll.total >= dc}),
};
load("browser-effect-removal.js");
load("browser-effect-removal-multi.js");
load("browser-effect-removal-slots.js");
const api = window.IRON_PIT_BROWSER_EFFECT_REMOVAL;
function member(id, side, spells = [], mods = [], resources = {}) {
  return {
    combatant_id: id, side, position_ft: 0,
    state: {
      is_alive: true, is_dead: false, action_available: true,
      resources, active_modifiers: mods,
      active_buff_effect_ids: mods.map((item) => item.source_effect_id),
      template: {
        name: id, ability_scores: {wisdom: 10},
        defensive_spell_actions: spells, spell_save_actions: [],
        spell_attack_actions: [], effect_tag_condition_grants: [],
      },
    },
  };
}
const action = {
  id: "dispel-magic", name: "Dispel Magic", level: 3, actionCost: "action",
  targetMode: "any", range: 120, castingAbility: "wisdom",
  autoRemoveMaxLevel: 3, removeAllTargetSpells: true,
  upcastSlotLevel: true, resourceId: "spell-slot-3",
  resourceCost: 1, expendsSpellSlot: true,
};
try {
  const actor = member("actor", "heroes", [], [], {"spell-slot-3": 1, "spell-slot-4": 1});
  actor.state.template.effect_removal_actions = [action];
  const target = member("target", "monsters", [{id: "ward", level: 4}],
    [{source_id: "target", source_effect_id: "ward"}]);
  const setup = {heroes: [actor], monsters: [target]};
  const picked = api.choose(actor, setup, "1:actor");
  assert.ok(picked);
  const event = api.resolve(1, 1, actor, setup, picked.action, picked.effect, "1:actor");
  assert.deepEqual(event.removed_condition_ids, ["ward"]);
  assert.equal(event.check_dc, null);
  assert.equal(actor.state.resources["spell-slot-3"], 1);
  assert.equal(actor.state.resources["spell-slot-4"], 0);
  assert.equal(target.state.active_modifiers.length, 0);
  assert.equal(actor.state.action_available, false);
  const third = member("third", "heroes", [], [], {"spell-slot-3": 1});
  third.state.template.effect_removal_actions = [action];
  const second = member("second", "monsters", [{id: "ward", level: 4}],
    [{source_id: "second", source_effect_id: "ward"}]);
  const p = api.choose(third, {heroes: [third], monsters: [second]}, "1:third");
  const fail = api.resolve(2, 1, third, {heroes: [third], monsters: [second]},
    p.action, p.effect, "1:third");
  assert.equal(fail.check_dc, 14);
  assert.equal(fail.check_succeeded, false);
  assert.equal(second.state.active_modifiers.length, 1);
  // A legal 4th-level slot works even when no level-3 slot remains.
  const onlyFourth = member("only-fourth", "heroes", [], [], {"spell-slot-3": 0, "spell-slot-4": 1});
  onlyFourth.state.template.effect_removal_actions = [action];
  const fourthWard = member("fourth-ward", "monsters", [{id: "ward", level: 4}],
    [{source_id: "fourth-ward", source_effect_id: "ward"}]);
  const fourthSetup = {heroes: [onlyFourth], monsters: [fourthWard]};
  const fourthPick = api.choose(onlyFourth, fourthSetup, "1:only-fourth");
  assert.ok(fourthPick, "Missing 3rd-level slot must not block a higher-slot cast");
  const fourthEvent = api.resolve(3, 1, onlyFourth, fourthSetup, fourthPick.action,
    fourthPick.effect, "1:only-fourth");
  assert.deepEqual(fourthEvent.removed_condition_ids, ["ward"]);
  assert.equal(onlyFourth.state.resources["spell-slot-4"], 0);
  console.log("2014 Dispel Magic upcast slot/threshold browser parity passed");
} catch (error) {
  console.error("2014 Dispel Magic upcast browser parity failed", error);
  process.exitCode = 1;
}
