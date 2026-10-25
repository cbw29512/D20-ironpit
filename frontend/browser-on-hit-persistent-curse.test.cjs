"use strict";
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

const S = window.IRON_PIT_BROWSER_STATE;
const O = window.IRON_PIT_BROWSER_ON_HIT_CONDITION_SAVE;
const C = window.IRON_PIT_BROWSER_CONDITION_REMOVAL;
const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];

function setDice(values) {
  try {
    const queue = [...values];
    window.IRON_PIT_DICE = {
      roll(sides) {
        try {
          const value = queue.shift();
          if (!(value >= 1 && value <= sides)) throw new Error("invalid d" + sides + ": " + value);
          return value;
        } catch (error) {
          console.error("Persistent-curse die roll failed.", { sides, error });
          throw error;
        }
      },
      rollMany(count, sides) {
        try {
          return Array.from({ length: count }, () => this.roll(sides));
        } catch (error) {
          console.error("Persistent-curse multi-roll failed.", { count, sides, error });
          throw error;
        }
      },
    };
  } catch (error) {
    console.error("Failed to configure persistent-curse dice.", { error });
    throw error;
  }
}

function member(id, side, position) {
  try {
    const template = structuredClone(base);
    Object.assign(template, {
      id: "template-" + id, name: id, armor_class: 10, max_hp: 40,
      saving_throw_bonuses: { ...template.saving_throw_bonuses, constitution: 0 },
      condition_immunities: [], condition_removal_actions: [], traits: [],
    });
    return { combatant_id: id, side, position_ft: position, state: S.buildState(template) };
  } catch (error) {
    console.error("Failed to build persistent-curse combatant.", { id, error });
    throw error;
  }
}

function effect(id = "synthetic-rot") {
  try {
    return {
      saveAbility: "constitution", dc: 12, conditionId: null,
      effectId: id, curseId: id, cannotRegainHitPoints: true,
      allowedRemovalActionIds: ["remove-curse"],
    };
  } catch (error) {
    console.error("Failed to build browser persistent curse.", { id, error });
    throw error;
  }
}

{
  const source = member("renamed-source", "monsters", 0);
  const target = member("renamed-target", "heroes", 5);
  const setup = { heroes: [target], monsters: [source] };
  setDice([1]);
  const result = O.resolve(target, { id: "renamed-hit", name: "Renamed Hit", onHitConditionSave: effect() },
    source.state.template, 1, setup, source);
  assert.equal(result.saveSucceeded, false);
  assert.deepEqual(target.state.active_curses, ["synthetic-rot"]);
  const active = target.state.timed_effects.find((item) => item.effect_id === "synthetic-rot");
  assert.ok(active);
  assert.equal(active.cannot_regain_hit_points, true);
  assert.deepEqual(active.owned_curse_ids, ["synthetic-rot"]);
  assert.equal(target.state.hit_point_maximum_reduction, 0);

  const remover = member("cleanser", "heroes", 0);
  remover.state.resources["spell-slot-3"] = 1;
  const removeCurse = {
    id: "remove-curse", name: "Remove Curse", actionCost: "action", range: 5,
    targetMode: "self_or_ally", removableConditions: [], maxConditionsPerUse: 1,
    resourceCosts: { "spell-slot-3": 1 }, resourceCostsPerCondition: {},
    expendsSpellSlot: true, removesAllCurses: true,
  };
  const removeSetup = { heroes: [remover, target], monsters: [] };
  const turnKey = "1:cleanser";
  const choice = C.chooseAction(remover, removeSetup, turnKey);
  assert.ok(choice);
  assert.deepEqual(choice.conditions, ["curse"]);
  C.resolve(1, 1, remover, target, removeCurse, ["curse"], turnKey);
  assert.deepEqual(target.state.active_curses, []);
  assert.equal(target.state.active_effect_ids.includes("synthetic-rot"), false);
  assert.equal(target.state.timed_effects.length, 0);
}

{
  const source = member("other-source", "monsters", 0);
  const target = member("other-target", "heroes", 5);
  const setup = { heroes: [target], monsters: [source] };
  setDice([20]);
  const result = O.resolve(target, { id: "other-hit", name: "Other Hit", onHitConditionSave: effect("other-curse") },
    source.state.template, 1, setup, source);
  assert.equal(result.saveSucceeded, true);
  assert.deepEqual(target.state.active_curses, []);
  assert.equal(target.state.timed_effects.length, 0);
}

console.log("Universal persistent failed-save curse lifecycle passed.");
