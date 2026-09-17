"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

load("browser-rolls.js");
load("browser-condition-rules.js");
load("browser-action-economy.js");
load("browser-modifiers.js");
load("browser-state.js");
load("browser-condition-immunity.js");
load("browser-timed-conditions.js");
load("browser-saves.js");
load("browser-turn-creature-effects.js");
load("browser-2014-paladin.js");

const S = window.IRON_PIT_BROWSER_STATE;
const M = window.IRON_PIT_BROWSER_MODIFIERS;
const P = window.IRON_PIT_BROWSER_PALADIN_2014;

function template(name, extra = {}) {
  return {
    id: name.toLowerCase(), name, class_id: null, archetype: name, level: 3, kind: "character",
    ruleset: "2014", size: "medium", max_hp: 30, speed_ft: 30, traits: [], resources: {},
    condition_immunities: [], ability_scores: { strength: 16, dexterity: 10, constitution: 14, intelligence: 8, wisdom: 12, charisma: 15 },
    saving_throw_bonuses: { strength: 3, dexterity: 0, constitution: 2, intelligence: -1, wisdom: 3, charisma: 4 },
    attacks: [{ id: "longsword-attack", weaponId: "longsword", name: "Longsword", kind: "melee", diceCount: 1, diceSize: 8, damageBonus: 3, damageType: "slashing" }],
    primary_attack_id: "longsword-attack", ...extra,
  };
}

function member(id, side, position, tpl) {
  return { combatant_id: id, side, position_ft: position, state: S.buildState(tpl) };
}

function queued(values) {
  const queue = [...values];
  window.IRON_PIT_DICE = {
    roll: () => { if (!queue.length) throw new Error("dice exhausted"); return queue.shift(); },
    rollMany: (count) => Array.from({ length: count }, () => { if (!queue.length) throw new Error("dice exhausted"); return queue.shift(); }),
  };
}

{
  const paladin = member("aurelia", "heroes", 0, template("Paladin", {
    class_id: "paladin", archetype: "Paladin", turn_unholy_2014: true,
    sacred_weapon_2014_bonus: 2, resources: { "channel-divinity": 1 },
  }));
  const commoner = member("commoner", "monsters", 5, template("Commoner", { kind: "monster", creature_type: "Humanoid" }));
  queued([10]);
  const result = P.resolveChannel(1, 1, paladin, { heroes: [paladin], monsters: [commoner] });
  assert.equal(result.sequence, 2);
  assert.equal(result.events[0].feature_id, "sacred-weapon");
  assert.equal(paladin.state.resources["channel-divinity"], 0);
  assert.equal(paladin.state.action_available, false);
  assert.equal(M.attackRollFlat(paladin.state, "longsword"), 2);
}

{
  const paladin = member("aurelia", "heroes", 0, template("Paladin", {
    class_id: "paladin", archetype: "Paladin", turn_unholy_2014: true,
    sacred_weapon_2014_bonus: 2, resources: { "channel-divinity": 1 },
  }));
  const skeleton = member("skeleton", "monsters", 10, template("Skeleton", { kind: "monster", creature_type: "Undead" }));
  const fiend = member("fiend", "monsters", 20, template("Fiend", { kind: "monster", creature_type: "Fiend" }));
  queued([1, 20]);
  const result = P.resolveChannel(1, 1, paladin, { heroes: [paladin], monsters: [skeleton, fiend] });
  assert.equal(result.sequence, 3);
  assert.deepEqual(result.events.map((event) => event.feature_id), ["turn-the-unholy", "turn-the-unholy"]);
  assert.deepEqual(result.events.map((event) => event.save_succeeded), [false, true]);
  assert.equal(result.events[0].save_dc, 12);
  assert.ok(skeleton.state.active_effect_ids.includes("turned-unholy"));
  assert.ok(skeleton.state.active_effect_ids.includes("frightened"));
  assert.ok(skeleton.state.active_effect_ids.includes("incapacitated"));
  assert.deepEqual(fiend.state.active_effect_ids, []);
  assert.equal(M.attackRollFlat(paladin.state, "longsword"), 0);
}

{
  const attacker = S.buildState(template("Paladin", {
    divine_smite_2014: true, resources: { "spell-slot-1": 1, "spell-slot-2": 1 },
  }));
  const defender = S.buildState(template("Skeleton", { kind: "monster", creature_type: "Undead" }));
  queued([4, 4, 4, 4]);
  const component = P.divineSmiteComponent(attacker, defender, attacker.template.attacks[0], false);
  assert.equal(component.notation, "4d8+0");
  assert.equal(component.total, 16);
  assert.equal(attacker.resources["spell-slot-2"], 0);
  assert.equal(attacker.resources["spell-slot-1"], 1);
}

{
  const attacker = S.buildState(template("Paladin", { divine_smite_2014: true, resources: { "spell-slot-1": 1 } }));
  const defender = S.buildState(template("Fiend", { kind: "monster", creature_type: "Fiend" }));
  queued([1, 1, 1, 1, 1, 1]);
  const component = P.divineSmiteComponent(attacker, defender, attacker.template.attacks[0], true);
  assert.equal(component.notation, "6d8+0");
  assert.equal(attacker.resources["spell-slot-1"], 0);
}

{
  const attacker = S.buildState(template("Paladin", { divine_smite_2014: true, resources: { "spell-slot-1": 1 } }));
  const defender = S.buildState(template("Target", { kind: "monster", creature_type: "Humanoid" }));
  const ranged = { ...attacker.template.attacks[0], kind: "ranged" };
  assert.equal(P.divineSmiteComponent(attacker, defender, ranged, false), null);
  assert.equal(attacker.resources["spell-slot-1"], 1);
}

console.log("2014 Paladin browser Channel Divinity and Divine Smite passed.");
