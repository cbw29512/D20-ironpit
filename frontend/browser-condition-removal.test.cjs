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
load("browser-spellcasting.js");
load("browser-state.js");
load("browser-timed-conditions.js");
load("browser-condition-removal-policy.js");
load("browser-condition-removal.js");
load("browser-delayed-effect-transition.js");

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
      grapple_sources: [], resources: { ...resources }, spell_slot_expended_turn_key: null,
      template: { name: id, condition_removal_actions: removals, condition_immunities: [] },
    },
  };
}

const key = (round, member) => `${round}:${member.combatant_id}`;
const layOnHands = {
  id: "lay-on-hands-poison", name: "Lay on Hands", actionCost: "bonus_action", range: 5,
  targetMode: "self_or_ally", removableConditions: ["poisoned"], maxConditionsPerUse: 1,
  resourceCosts: {}, resourceCostsPerCondition: { "lay-on-hands": 5 }, expendsSpellSlot: false,
};
const lesserRestoration = {
  id: "lesser-restoration", name: "Lesser Restoration", actionCost: "bonus_action", range: 5,
  targetMode: "self_or_ally", removableConditions: ["blinded", "deafened", "paralyzed", "poisoned"],
  maxConditionsPerUse: 1, resourceCosts: { "spell-slot-2": 1 }, resourceCostsPerCondition: {},
  expendsSpellSlot: true,
};

{
  const remover = member("paladin", [], { "lay-on-hands": 5 }, [layOnHands]);
  const ally = member("ally", ["poisoned"]);
  const setup = { heroes: [remover, ally], monsters: [] }, turnKey = key(1, remover);
  const choice = C.chooseAction(remover, setup, turnKey);
  assert.equal(choice.target, ally);
  assert.deepEqual(choice.conditions, ["poisoned"]);
  const event = C.resolve(1, 1, remover, ally, choice.action, choice.conditions, turnKey);
  assert.equal(remover.state.bonus_action_available, false);
  assert.equal(remover.state.resources["lay-on-hands"], 0);
  assert.deepEqual(ally.state.active_effect_ids, []);
  assert.deepEqual(event.removed_condition_ids, ["poisoned"]);
}

{
  const remover = member("cleric", [], { "spell-slot-2": 1 }, [lesserRestoration]);
  const ally = member("ally", ["poisoned", "paralyzed"]);
  const setup = { heroes: [remover, ally], monsters: [] }, turnKey = key(1, remover);
  const choice = C.chooseAction(remover, setup, turnKey);
  assert.deepEqual(choice.conditions, ["paralyzed"]);
  C.resolve(1, 1, remover, ally, choice.action, choice.conditions, turnKey);
  assert.deepEqual(ally.state.active_effect_ids, ["poisoned"]);
  assert.equal(remover.state.resources["spell-slot-2"], 0);
  assert.equal(remover.state.spell_slot_expended_turn_key, turnKey);
}

{
  const actionSpell = {
    id: "action-slot-cleanse", name: "Action Slot Cleanse", actionCost: "action", range: 5,
    targetMode: "self_or_ally", removableConditions: ["blinded"], maxConditionsPerUse: 1,
    resourceCosts: { "spell-slot-3": 1 }, resourceCostsPerCondition: {}, expendsSpellSlot: true,
  };
  const remover = member("caster", [], { "spell-slot-2": 1, "spell-slot-3": 1 }, [lesserRestoration, actionSpell]);
  const ally = member("ally", ["paralyzed", "blinded"]);
  const setup = { heroes: [remover, ally], monsters: [] }, firstTurn = key(1, remover);
  const first = C.chooseAction(remover, setup, firstTurn);
  C.resolve(1, 1, remover, ally, first.action, first.conditions, firstTurn);
  assert.equal(remover.state.action_available, true, "Action remains free after the Bonus Action spell");
  assert.equal(C.chooseAction(remover, setup, firstTurn), null, "A second slot spell is illegal on the same 2024 turn");
  remover.state.action_available = true; remover.state.bonus_action_available = true;
  const second = C.chooseAction(remover, setup, key(2, remover));
  assert.equal(second.action.id, "action-slot-cleanse");
}

{
  const remover = member("cleric", [], {}, [lesserRestoration]);
  const ally = member("ally", ["stunned"]);
  assert.equal(C.chooseAction(remover, { heroes: [remover, ally], monsters: [] }, key(1, remover)), null);
}

{
  const generic = { ...layOnHands, id: "generic-cleanse", resourceCostsPerCondition: {} };
  const remover = member("cleanser", [], {}, [generic]);
  const ally = member("ally", ["poisoned"]);
  ally.state.timed_effects = [{
    effect_id: "poisoned", source_id: "restricted-source", allowed_removal_action_ids: ["specific-cleanse"],
  }];
  assert.equal(C.chooseAction(remover, { heroes: [remover, ally], monsters: [] }, key(1, remover)), null);
}

{
  const reaction = {
    ...layOnHands, id: "triggered-cleanse", actionCost: "reaction",
    resourceCostsPerCondition: {}, reactionTrigger: "condition_applied_to_ally",
  };
  const remover = member("reactor", [], {}, [reaction]);
  const ally = member("ally", ["poisoned"]);
  const setup = { heroes: [remover, ally], monsters: [] }, turnKey = "1:enemy-turn";
  assert.equal(C.chooseAction(remover, setup, turnKey), null, "reaction options must never fire as normal turn actions");
  assert.ok(C.chooseReaction(remover, setup, "condition_applied_to_ally", ally, turnKey));
  assert.equal(C.chooseReaction(remover, setup, "condition_applied_to_self", ally, turnKey), null);
}

{
  const removeCurse = {
    id: "generic-curse-removal", name: "Generic Curse Removal", actionCost: "action", range: 5,
    targetMode: "self_or_ally", removableConditions: [], maxConditionsPerUse: 1,
    resourceCosts: {}, resourceCostsPerCondition: {}, expendsSpellSlot: false, removesAllCurses: true,
  };
  const remover = member("curse-cleanser", [], {}, [removeCurse]);
  const ally = member("curse-target");
  ally.state.active_curses = ["synthetic-rot"];
  ally.state.active_effect_ids = ["synthetic-rot"];
  ally.state.timed_effects = [{
    effect_id: "synthetic-rot", source_id: "renamed-source", source_effect_id: "Renamed Hit",
    allowed_removal_action_ids: ["remove-curse"], owned_curse_ids: ["synthetic-rot"],
    cannot_regain_hit_points: true,
  }];
  const setup = { heroes: [remover, ally], monsters: [] }, turnKey = key(1, remover);
  const choice = C.chooseAction(remover, setup, turnKey);
  assert.ok(choice);
  assert.deepEqual(choice.conditions, ["curse"]);
  C.resolve(1, 1, remover, ally, choice.action, choice.conditions, turnKey);
  assert.deepEqual(ally.state.active_curses, []);
  assert.deepEqual(ally.state.active_effect_ids, []);
  assert.deepEqual(ally.state.timed_effects, []);
}


{
  const lesser = {
    id: "lesser-restoration", name: "Lesser Restoration", actionCost: "action", range: 5,
    targetMode: "self_or_ally", removableConditions: [], removalEffectTags: ["disease"],
    spellLevel: 2, maxConditionsPerUse: 1, resourceCosts: {}, resourceCostsPerCondition: {},
  };
  const greater = { ...lesser, id: "greater-restoration", spellLevel: 6 };
  const heal = { ...lesser, id: "heal", removalEffectTags: [], spellLevel: 0 };
  const remover = member("cleanser", [], {}, [lesser]);
  const ally = member("ally", ["renamed-disease"]);
  ally.state.timed_effects = [{
    effect_id: "renamed-disease", source_id: "renamed-source",
    removal_effect_tag: "disease", minimum_removal_spell_level: 6,
    removal_action_exceptions: ["heal"],
  }];
  const setup = { heroes: [remover, ally], monsters: [] }, turnKey = key(1, remover);
  assert.equal(C.chooseAction(remover, setup, turnKey), null);
  remover.state.template.condition_removal_actions = [greater];
  assert.ok(C.chooseAction(remover, setup, turnKey));
  remover.state.template.condition_removal_actions = [heal];
  assert.ok(C.chooseAction(remover, setup, turnKey));
}

{
  const target = member("delayed-target", ["diseased"]);
  target.state.turns_started = 0;
  target.state.timed_effects[0].source_effect_id = "Renamed Hit";
  const rule = {
    removalEffectTag: "disease", minimumRemovalSpellLevel: 0,
    removalActionExceptions: [],
    delayedTransition: {
      targetTurns: 10, cannotRegainHitPoints: true, removalEffectTag: "disease",
      minimumRemovalSpellLevel: 6, removalActionExceptions: ["heal"],
    },
  };
  const D = window.IRON_PIT_BROWSER_DELAYED_EFFECT_TRANSITION;
  D.schedule(target.state, "diseased", "enemy", "Renamed Hit", rule);
  target.state.turns_started = 9;
  assert.equal(D.activateDue(1, 9, target).events.length, 0);
  target.state.turns_started = 10;
  const activated = D.activateDue(1, 10, target);
  assert.equal(activated.events.length, 1);
  assert.equal(target.state.timed_effects[0].cannot_regain_hit_points, true);
  assert.equal(target.state.timed_effects[0].minimum_removal_spell_level, 6);
  assert.deepEqual(target.state.timed_effects[0].removal_action_exceptions, ["heal"]);
  assert.equal(D.activateDue(activated.sequence, 11, target).events.length, 0);
}

console.log("Browser 2024 condition-removal regressions passed.");
