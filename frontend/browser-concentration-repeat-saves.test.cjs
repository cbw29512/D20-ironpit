"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => Boolean(state[`${cost}_available`]),
  spend: (state, cost) => { state[`${cost}_available`] = false; },
};
window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS = {
  removeOwnerAttackEnding: () => {},
};

let fixedSlotSeen = null;
window.IRON_PIT_BROWSER_SPELL_POLICY = {
  chooseActionAtSlot: (_member, _setup, spell, slotLevel) => {
    fixedSlotSeen = slotLevel;
    return {
      action: spell,
      slotLevel,
      targetIds: ["target"],
      placement: null,
      expectedDamage: 17,
    };
  },
};

let effectCalls = 0;
window.IRON_PIT_BROWSER_SPELL_RESOLUTION = {
  resolveEffect: (sequence, _round, _member, _setup, choice) => {
    effectCalls += 1;
    assert.equal(choice.slotLevel, 4);
    return {
      events: [{ sequence, event_type: "saving_throw", feature_id: choice.action.id }],
      sequence: sequence + 1,
    };
  },
};

load("browser-concentration-repeat-saves.js");

const originalTemplate = {
  id: "caster-original",
  name: "Caster",
  spell_save_actions: [{
    id: "storm-pulse",
    name: "Storm Pulse",
    level: 3,
    actionCost: "action",
    concentration: true,
  }],
  concentration_repeat_save_actions: [{
    id: "storm-pulse-repeat",
    name: "Storm Pulse",
    sourceSpellId: "storm-pulse",
    actionCost: "action",
    priority: 80,
    animation: "spell-save",
  }],
};
const member = {
  combatant_id: "caster",
  side: "heroes",
  state: {
    action_available: true,
    concentration: {
      effect_id: "storm-pulse",
      slot_level: 4,
    },
    resources: { "spell-slot-4": 1 },
    template: {
      id: "caster-form",
      name: "Caster",
      spell_save_actions: [],
      concentration_repeat_save_actions: [],
    },
    replacement_form: {
      original_template: originalTemplate,
    },
  },
};
const target = {
  combatant_id: "target",
  side: "monsters",
  state: { current_hp: 20, is_alive: true, is_dead: false },
};
const setup = { heroes: [member], monsters: [target] };

const selected = window.IRON_PIT_BROWSER_CONCENTRATION_REPEAT_SAVES.choose(member, setup);
assert.ok(selected);
assert.equal(selected.action.id, "storm-pulse-repeat");
assert.equal(selected.spellChoice.action.id, "storm-pulse");
assert.equal(fixedSlotSeen, 4);

const result = window.IRON_PIT_BROWSER_CONCENTRATION_REPEAT_SAVES.resolve(
  1, 2, member, setup, "2:caster", selected,
);

assert.equal(member.state.action_available, false);
assert.equal(member.state.resources["spell-slot-4"], 1);
assert.equal(member.state.concentration.effect_id, "storm-pulse");
assert.equal(effectCalls, 1);
assert.equal(result.events[0].feature_id, "storm-pulse-repeat");
assert.equal(result.events[1].feature_id, "storm-pulse");

console.log("Browser concentration repeat-save actions preserve slots and work through replacement forms.");
