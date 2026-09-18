"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

load("browser-rolls.js");
load("browser-condition-rules.js");
load("browser-action-economy.js");
load("browser-modifiers.js");
load("browser-state.js");
load("browser-defensive-modifier-rules.js");
load("browser-condition-immunity.js");
load("browser-concentration.js");
load("browser-spell-modifiers.js");
load("browser-timed-conditions.js");
load("browser-saves.js");
load("browser-targeting-wards.js");
load("browser-spellcasting.js");
load("browser-healing.js");
load("browser-condition-removal.js");
load("browser-effect-removal.js");
load("browser-turn.js");
load("browser-precombat-spells.js");

const S = window.IRON_PIT_BROWSER_STATE;
const M = window.IRON_PIT_BROWSER_MODIFIERS;
const DM = window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS;
const I = window.IRON_PIT_BROWSER_CONDITION_IMMUNITY;
const SM = window.IRON_PIT_BROWSER_SPELL_MODIFIERS;
const W = window.IRON_PIT_BROWSER_TARGETING_WARDS;
const H = window.IRON_PIT_BROWSER_HEALING;
const CR = window.IRON_PIT_BROWSER_CONDITION_REMOVAL;
const ER = window.IRON_PIT_BROWSER_EFFECT_REMOVAL;
const TURN = window.IRON_PIT_BROWSER_TURN;
const PRE = window.IRON_PIT_BROWSER_PRECOMBAT_SPELLS;

function template(name, extra = {}) {
  return {
    id: name.toLowerCase().replaceAll(" ", "-"), name, class_id: null, archetype: name,
    level: 9, kind: "character", ruleset: "2014", size: "medium",
    armor_class: 15, max_hp: 30, speed_ft: 30, initiative_bonus: 0,
    condition_immunities: [], traits: [], resources: {},
    ability_scores: { strength: 16, dexterity: 10, constitution: 14, intelligence: 8, wisdom: 12, charisma: 16 },
    saving_throw_bonuses: { strength: 3, dexterity: 0, constitution: 2, intelligence: -1, wisdom: 1, charisma: 5 },
    attacks: [{ id: "sword", weaponId: "sword", name: "Sword", kind: "melee", bonus: 5,
      diceCount: 1, diceSize: 8, damageBonus: 3, damageType: "slashing", reach: 5 }],
    primary_attack_id: "sword", defensive_spell_actions: [], healingActions: [],
    condition_removal_actions: [], effect_removal_actions: [],
    ...extra,
  };
}

function member(id, side, position, tpl) {
  return { combatant_id: id, side, position_ft: position, state: S.buildState(tpl) };
}

function queued(values) {
  const queue = [...values];
  window.IRON_PIT_DICE = {
    roll: () => {
      if (!queue.length) throw new Error("dice exhausted");
      return queue.shift();
    },
    rollMany: (count) => Array.from({ length: count }, () => {
      if (!queue.length) throw new Error("dice exhausted");
      return queue.shift();
    }),
  };
}

const protectedTypes = ["aberration", "celestial", "elemental", "fey", "fiend", "undead"];
const protection = {
  id: "protection-from-evil-and-good", name: "Protection from Evil and Good",
  level: 1, actionCost: "action", range: 5, durationMinutes: 10,
  targetPolicy: "friendly", targetCount: 1, concentration: true, priority: 38,
  modifierEffects: [
    { kind: "attacks-against-disadvantage", sourceCreatureTypes: protectedTypes },
    { kind: "condition-immunity", conditionId: "charmed", sourceCreatureTypes: protectedTypes },
    { kind: "condition-immunity", conditionId: "frightened", sourceCreatureTypes: protectedTypes },
  ],
};
const sanctuary = {
  id: "sanctuary", name: "Sanctuary", level: 1, actionCost: "bonus_action",
  range: 30, durationMinutes: 1, targetPolicy: "friendly", targetCount: 1,
  concentration: false, priority: 32,
  modifierEffects: [{ kind: "targeting-save-gate", saveAbility: "wisdom", saveDc: 13, endsOnOwnerAttack: true }],
};
const beacon = {
  id: "beacon-of-hope", name: "Beacon of Hope", level: 3, actionCost: "action",
  range: 30, durationMinutes: 1, targetPolicy: "friendly", targetCount: 20,
  concentration: true, priority: 60,
  modifierEffects: [
    { kind: "saving-throw-advantage", saveAbility: "wisdom" },
    { kind: "death-save-advantage" },
    { kind: "healing-maximize" },
  ],
};

{
  const caster = member("caster", "heroes", 0, template("Caster"));
  const ally = member("ally", "heroes", 5, template("Ally"));
  SM.apply(caster.state, [{ targetId: ally.combatant_id, state: ally.state }], caster.combatant_id, protection, 0, [caster.state, ally.state]);
  assert.equal(DM.attacksAgainstDisadvantage(ally.state, template("Fiend", { creature_type: "Fiend" })), 1);
  assert.equal(DM.attacksAgainstDisadvantage(ally.state, template("Human", { creature_type: "Humanoid" })), 0);
  assert.equal(I.immune(ally.state, "charmed", template("Fiend", { creature_type: "Fiend" })), true);
  assert.equal(I.immune(ally.state, "charmed", template("Human", { creature_type: "Humanoid" })), false);
}

{
  const caster = member("caster", "heroes", 0, template("Caster"));
  const ally = member("ally", "heroes", 5, template("Ally"));
  const enemy = member("enemy", "monsters", 10, template("Enemy", { kind: "monster" }));
  SM.apply(caster.state, [{ targetId: ally.combatant_id, state: ally.state }], caster.combatant_id, sanctuary, 0, [caster.state, ally.state, enemy.state]);
  queued([1]);
  const ward = W.check(enemy, ally);
  assert.equal(ward.succeeded, false);
  assert.equal(ward.gate.source_effect_id, "sanctuary");

  const owner = member("owner", "heroes", 0, template("Owner"));
  SM.apply(owner.state, [{ targetId: owner.combatant_id, state: owner.state }], owner.combatant_id, sanctuary, 0, [owner.state, enemy.state]);
  assert.ok(owner.state.active_modifiers.some((item) => item.source_effect_id === "sanctuary"));
  assert.equal(W.check(owner, enemy), null);
  assert.ok(!owner.state.active_modifiers.some((item) => item.source_effect_id === "sanctuary"));
}

{
  const caster = member("caster", "heroes", 0, template("Caster"));
  const ally = member("ally", "heroes", 5, template("Ally"));
  SM.apply(caster.state, [{ targetId: ally.combatant_id, state: ally.state }], caster.combatant_id, beacon, 0, [caster.state, ally.state]);
  assert.equal(window.IRON_PIT_BROWSER_SAVES.saveMode(ally.state, "wisdom"), "advantage");

  ally.state.current_hp = 0;
  ally.state.is_unconscious = true;
  queued([2, 15]);
  const death = TURN.deathSave(1, 1, ally);
  assert.equal(death.death_save_roll.mode, "advantage");
  assert.equal(death.death_save_roll.selected_roll, 15);

  const healer = member("healer", "heroes", 0, template("Healer", { resources: { "spell-slot-1": 1 } }));
  ally.state.current_hp = 1;
  ally.state.is_unconscious = false;
  const cure = { id: "cure-wounds", name: "Cure Wounds", actionCost: "action", range: 5,
    targetMode: "self_or_ally", diceCount: 1, diceSize: 8, healingBonus: 3,
    resourceId: "spell-slot-1", resourceCost: 1, animation: "healing" };
  queued([1]);
  const heal = H.resolve(2, 1, healer, ally, cure, "1:healer");
  assert.deepEqual(heal.healing_roll.rolls, [8]);
  assert.equal(heal.healing_roll.total, 11);
}

{
  const remover = member("paladin", "heroes", 0, template("Paladin", { resources: { "spell-slot-2": 1 } }));
  const ally = member("ally", "heroes", 5, template("Ally"));
  ally.state.active_effect_ids.push("poisoned");
  const lesser = {
    id: "lesser-restoration", name: "Lesser Restoration", actionCost: "action", range: 5,
    targetMode: "self_or_ally", removableConditions: ["blinded", "deafened", "paralyzed", "poisoned"],
    maxConditionsPerUse: 1, resourceCosts: { "spell-slot-2": 1 }, resourceCostsPerCondition: {},
    expendsSpellSlot: true, animation: "lesser-restoration",
  };
  const event = CR.resolve(1, 1, remover, ally, lesser, ["poisoned"], "1:paladin");
  assert.deepEqual(event.removed_condition_ids, ["poisoned"]);
  assert.equal(remover.state.action_available, false);
  assert.equal(remover.state.resources["spell-slot-2"], 0);
}

{
  const dispel = {
    id: "dispel-magic", name: "Dispel Magic", level: 3, actionCost: "action", range: 120,
    castingAbility: "charisma", targetMode: "enemy", autoRemoveMaxLevel: 3,
    resourceId: "spell-slot-3", resourceCost: 1, expendsSpellSlot: true, animation: "dispel-magic",
  };
  const lowSpell = { ...sanctuary, level: 1 };
  const source = member("source", "monsters", 10, template("Source", { defensive_spell_actions: [lowSpell] }));
  const remover = member("remover", "heroes", 0, template("Remover", {
    resources: { "spell-slot-3": 1 }, effect_removal_actions: [dispel],
  }));
  SM.apply(source.state, [{ targetId: source.combatant_id, state: source.state }], source.combatant_id, lowSpell, 0, [source.state, remover.state]);
  const setup = { heroes: [remover], monsters: [source] };
  const choice = ER.choose(remover, setup, "1:remover");
  assert.ok(choice);
  const event = ER.resolve(1, 1, remover, setup, choice.action, choice.effect, "1:remover");
  assert.equal(event.check_dc, null);
  assert.deepEqual(event.removed_condition_ids, ["sanctuary"]);
  assert.equal(source.state.active_modifiers.length, 0);

  const highSpell = {
    id: "level-four-ward", name: "Level Four Ward", level: 4, actionCost: "action",
    range: 5, durationMinutes: 1, targetPolicy: "self", targetCount: 1,
    concentration: false, modifierEffects: [{ kind: "armor-class", flatBonus: 1 }],
  };
  const high = member("high", "monsters", 10, template("High", { defensive_spell_actions: [highSpell] }));
  const remover2 = member("remover2", "heroes", 0, template("Remover 2", {
    resources: { "spell-slot-3": 1 }, effect_removal_actions: [dispel],
  }));
  SM.apply(high.state, [{ targetId: high.combatant_id, state: high.state }], high.combatant_id, highSpell, 0, [high.state, remover2.state]);
  queued([1]);
  const choice2 = ER.choose(remover2, { heroes: [remover2], monsters: [high] }, "1:remover2");
  const failed = ER.resolve(1, 1, remover2, { heroes: [remover2], monsters: [high] }, choice2.action, choice2.effect, "1:remover2");
  assert.equal(failed.check_dc, 14);
  assert.equal(failed.check_succeeded, false);
  assert.equal(high.state.active_modifiers.length, 1);
}

{
  const paladin = member("paladin", "heroes", 0, template("Paladin", {
    defensive_spell_actions: [protection, sanctuary],
    resources: { "spell-slot-1": 2 },
  }));
  const humanoid = member("humanoid", "monsters", 10, template("Humanoid", { kind: "monster", creature_type: "Humanoid" }));
  assert.equal(PRE.typedRelevant(paladin, { heroes: [paladin], monsters: [humanoid] }, protection), false);
  const fiend = member("fiend", "monsters", 10, template("Fiend", { kind: "monster", creature_type: "Fiend" }));
  assert.equal(PRE.typedRelevant(paladin, { heroes: [paladin], monsters: [fiend] }, protection), true);
}

console.log("2014 Devotion Paladin oath-spell browser parity passed.");
