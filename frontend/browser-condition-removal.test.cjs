"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
load("browser-condition-immunity.js");
load("browser-condition-rules.js");
load("browser-action-economy.js");
load("browser-condition-removal.js");

const C = window.IRON_PIT_BROWSER_CONDITION_REMOVAL;

function member(id, conditions = [], resources = {}, removals = []) {
  return {
    combatant_id: id,
    side: "heroes",
    position_ft: 0,
    state: {
      current_hp: 10, is_alive: true, is_dead: false, is_unconscious: false,
      action_available: true, bonus_action_available: true, reaction_available: true,
      active_effect_ids: [...conditions], timed_effects: conditions.map((effect_id) => ({ effect_id, source_id: "enemy" })),
      grapple_sources: [], resources: { ...resources },
      template: { name: id, condition_removal_actions: removals, condition_immunities: [] },
    },
  };
}

const layOnHands = {
  id: "lay-on-hands-poison", name: "Lay on Hands", actionCost: "bonus_action", range: 5,
  targetMode: "self_or_ally", removableConditions: ["poisoned"], maxConditionsPerUse: 1,
  resourceCosts: {}, resourceCostsPerCondition: { "lay-on-hands": 5 },
};
const lesserRestoration = {
  id: "lesser-restoration", name: "Lesser Restoration", actionCost: "bonus_action", range: 5,
  targetMode: "self_or_ally", removableConditions: ["blinded", "deafened", "paralyzed", "poisoned"],
  maxConditionsPerUse: 1, resourceCosts: { "spell-slot-2": 1 }, resourceCostsPerCondition: {},
};

{
  const remover = member("paladin", [], { "lay-on-hands": 5 }, [layOnHands]);
  const ally = member("ally", ["poisoned"]);
  const setup = { heroes: [remover, ally], monsters: [] };
  const choice = C.chooseAction(remover, setup);
  assert.equal(choice.target, ally);
  assert.deepEqual(choice.conditions, ["poisoned"]);
  const event = C.resolve(1, 1, remover, ally, choice.action, choice.conditions);
  assert.equal(remover.state.bonus_action_available, false);
  assert.equal(remover.state.resources["lay-on-hands"], 0);
  assert.deepEqual(ally.state.active_effect_ids, []);
  assert.deepEqual(event.removed_condition_ids, ["poisoned"]);
}

{
  const remover = member("cleric", [], { "spell-slot-2": 1 }, [lesserRestoration]);
  const ally = member("ally", ["poisoned", "paralyzed"]);
  const setup = { heroes: [remover, ally], monsters: [] };
  const choice = C.chooseAction(remover, setup);
  assert.deepEqual(choice.conditions, ["paralyzed"]);
  C.resolve(1, 1, remover, ally, choice.action, choice.conditions);
  assert.deepEqual(ally.state.active_effect_ids, ["poisoned"]);
  assert.equal(remover.state.resources["spell-slot-2"], 0);
}

{
  const remover = member("cleric", [], {}, [lesserRestoration]);
  const ally = member("ally", ["stunned"]);
  assert.equal(C.chooseAction(remover, { heroes: [remover, ally], monsters: [] }), null);
}

{
  const reaction = {
    ...layOnHands, id: "triggered-cleanse", actionCost: "reaction",
    resourceCostsPerCondition: {}, reactionTrigger: "condition_applied_to_ally",
  };
  const remover = member("reactor", [], {}, [reaction]);
  const ally = member("ally", ["poisoned"]);
  const setup = { heroes: [remover, ally], monsters: [] };
  assert.equal(C.chooseAction(remover, setup), null, "reaction options must never fire as normal turn actions");
  assert.ok(C.chooseReaction(remover, setup, "condition_applied_to_ally", ally));
  assert.equal(C.chooseReaction(remover, setup, "condition_applied_to_self", ally), null);
}

console.log("Browser 2024 condition-removal regressions passed.");
