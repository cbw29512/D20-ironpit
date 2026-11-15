"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (file) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, file), "utf8"), {filename: file},
);
window.IRON_PIT_BROWSER_STATE = {distance: (a, b) => Math.abs(a.position_ft - b.position_ft)};
window.IRON_PIT_ACTION_ECONOMY = {
  available: (s, cost) => cost === "action" && s.action_available,
  spend: (s) => {s.action_available = false;},
};
window.IRON_PIT_BROWSER_SPELLCASTING = {
  slotSpellAvailable: () => true,
  markSlotSpellCast: (s) => {s.slot_spell_cast = true;},
};
window.IRON_PIT_BROWSER_MODIFIERS = {
  removeSource: (states, source, spell) => {
    for (const state of states) state.active_modifiers = state.active_modifiers.filter(
      (mod) => mod.source_id !== source || mod.source_effect_id !== spell,
    );
  },
};
const rolls = [4, 18];
window.IRON_PIT_BROWSER_ROLLS = {d20: (bonus) => {
  const die = rolls.shift();
  if (!Number.isInteger(die)) throw new Error("Unexpected additional d20 roll");
  return {notation: "1d20", rolls: [die], selected_roll: die, modifier: bonus, total: die + bonus};
}};
window.IRON_PIT_BROWSER_ABILITY_CHECKS = {
  mode: () => "normal",
  resolve: (_state, _ability, roll, dc) => ({roll, succeeded: roll.total >= dc}),
};
load("browser-effect-removal.js");
load("browser-effect-removal-multi.js");
const api = window.IRON_PIT_BROWSER_EFFECT_REMOVAL;

function member(id, side, spells = [], modifiers = []) {
  return {
    combatant_id: id, side, position_ft: 0,
    state: {
      action_available: true, is_alive: true, is_dead: false,
      resources: {"spell-slot-3": 1},
      active_modifiers: modifiers,
      active_buff_effect_ids: modifiers.map((m) => m.source_effect_id),
      template: {
        name: id, ability_scores: {intelligence: 10},
        defensive_spell_actions: spells, spell_save_actions: [],
        spell_attack_actions: [], effect_tag_condition_grants: [],
      },
    },
  };
}
const spell = (id, level) => ({id, level});
const mod = (id) => ({source_id: "source", source_effect_id: id});
try {
  const actor = member("actor", "heroes");
  const source = member("source", "monsters", [
    spell("bless", 1), spell("haste", 3),
    spell("greater-invisibility", 4), spell("stoneskin", 4),
  ]);
  const target = member("target", "monsters", [], [
    mod("bless"), mod("haste"), mod("greater-invisibility"),
    mod("stoneskin"), mod("natural-armor"),
  ]);
  const other = member("other", "monsters", [], [mod("haste")]);
  const setup = {heroes: [actor], monsters: [source, target, other]};
  const action = {
    id: "dispel-magic", name: "Dispel Magic",
    targetMode: "any", actionCost: "action", range: 120,
    autoRemoveMaxLevel: 3, removeAllTargetSpells: true,
    castingAbility: "intelligence", resourceId: "spell-slot-3",
    resourceCost: 1, expendsSpellSlot: true,
  };
  actor.state.template.effect_removal_actions = [action];
  const choice = api.choose(actor, setup, "1:actor");
  assert.equal(choice.effect.target.combatant_id, "target");
  const event = api.resolve(1, 1, actor, setup, action, choice.effect, "1:actor");
  assert.deepEqual(new Set(event.removed_condition_ids),
    new Set(["stoneskin", "haste", "bless"]));
  assert.match(event.description, /greater-invisibility: resisted/);
  assert.equal(event.audit.steps.length, 4);
  assert.equal(event.check_dc, 14);
  assert.equal(event.check_succeeded, false);
  assert.equal(actor.state.action_available, false);
  assert.equal(actor.state.resources["spell-slot-3"], 0);
  assert.equal(actor.state.slot_spell_cast, true);
  assert.deepEqual(target.state.active_modifiers.map((m) => m.source_effect_id),
    ["greater-invisibility", "natural-armor"]);
  assert.deepEqual(other.state.active_modifiers.map((m) => m.source_effect_id), ["haste"]);
  console.log("2014 Dispel Magic browser multi-effect checks and resource parity passed");
} catch (error) {
  console.error("2014 Dispel Magic multi-effect browser regression failed", error);
  process.exitCode = 1;
}
