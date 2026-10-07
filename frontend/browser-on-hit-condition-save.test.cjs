"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const htmlPath of [path.join(__dirname, "index.html"), path.join(__dirname, "..", "index.html")]) {
  const html = fs.readFileSync(htmlPath, "utf8");
  assert.match(html, /browser-on-hit-condition-save\.js/, `${htmlPath} must load shared on-hit condition-save rules`);
  assert.ok(html.indexOf("browser-on-hit-condition-save.js") < html.indexOf("browser-saves.js"));
}
for (const file of [
  "browser-heroes.js", "browser-monsters-2014.js", "browser-condition-immunity.js", "browser-condition-rules.js",
  "browser-action-economy.js", "browser-grapple.js", "browser-modifier-validation.js", "browser-modifiers.js",
  "browser-state.js", "browser-rage.js", "browser-sneak-attack.js", "browser-rolls.js", "browser-undead-fortitude.js",
  "browser-terminal-effects.js", "browser-zero-hp.js", "browser-timed-conditions.js", "browser-weapon-mastery.js", "browser-ability-hooks.js",
  "browser-attack-outcome.js", "browser-attack.js", "browser-saving-throws.js", "browser-on-hit-condition-save.js",
  "browser-saves.js", "browser-condition-lifecycle.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];
const attackShape = {
  id: "greatsword-attack", weaponId: "greatsword", name: "Greatsword", kind: "melee",
  bonus: 5, diceCount: 2, diceSize: 6, damageBonus: 3, damageType: "slashing", reach: 5,
  animation: "slash", attackAbility: "strength", attackAbilityModifier: 3, onHitDamage: [],
};

function dice(values) {
  const rolls = [...values];
  window.IRON_PIT_DICE = {
    roll(sides) { const value = rolls.shift(); if (!(value >= 1 && value <= sides)) throw new Error(`invalid d${sides}: ${value}`); return value; },
    rollMany(count, sides) { return Array.from({ length: count }, () => this.roll(sides)); },
  };
}
function member(id, side, options = {}) {
  const template = structuredClone(base);
  Object.assign(template, {
    id: `template-${id}`, name: id, level: 1, armor_class: options.armorClass ?? 10,
    max_hp: 40, attacks: [structuredClone(attackShape)], primary_attack_id: attackShape.id,
    weapon_masteries: [], traits: [], size: options.size || "medium",
    creature_type: options.creatureType || template.creature_type,
    condition_immunities: options.immune || [],
    saving_throw_bonuses: { ...template.saving_throw_bonuses, constitution: 0, strength: 0 },
  });
  if (options.onHitConditionSave) template.attacks[0].onHitConditionSave = options.onHitConditionSave;
  return { combatant_id: id, side, position_ft: options.position ?? 0, state: S.buildState(template) };
}
function attack(attacker, target, values) {
  dice(values);
  return window.IRON_PIT_BROWSER_ATTACK.resolveAttack(1, 1, attacker, target, attacker.state.template.attacks[0], 5, { spendAction: false });
}

{
  const fighter = member("fighter", "heroes", {
    onHitConditionSave: { saveAbility: "constitution", dc: 12, conditionId: "poisoned" },
  });
  const target = member("target", "monsters", { position: 5 });
  const event = attack(fighter, target, [15, 4, 4, 4]);
  assert.equal(event.hit, true);
  assert.equal(event.save_ability, "constitution");
  assert.equal(event.save_dc, 12);
  assert.equal(event.save_succeeded, false);
  assert.ok(event.applied_condition_ids.includes("poisoned"));
  assert.ok(target.state.active_effect_ids.includes("poisoned"));
  assert.match(event.description, /HIT with Greatsword/);
  assert.match(event.description, /Poisoned/);
}

{
  const fighter = member("fighter", "heroes", {
    onHitConditionSave: {
      saveAbility: "constitution", dc: 10, conditionId: "paralyzed",
      durationRounds: 10, repeatSaveTiming: "target_turn_end",
      excludedCreatureTypes: ["undead"], excludedCreatureSubtypes: ["elf"],
    },
  });
  const target = member("target", "monsters", { position: 5 });
  const event = attack(fighter, target, [15, 4, 4, 3]);
  assert.equal(event.save_succeeded, false);
  assert.ok(event.applied_condition_ids.includes("paralyzed"));
  assert.ok(target.state.active_effect_ids.includes("paralyzed"));
  const timed = target.state.timed_effects.find((item) => item.effect_id === "paralyzed");
  assert.ok(timed);
  assert.equal(timed.repeat_save_ability, "constitution");
  assert.equal(timed.repeat_save_dc, 10);
  assert.equal(timed.repeat_save_timing, "target_turn_end");
  assert.equal(timed.expires_round, 11);
  assert.equal(timed.source_effect_id, "Greatsword");
  assert.match(event.description, /Paralyzed/);
  const undead = member("undead", "monsters", { position: 5, creatureType: "undead" });
  const elf = member("elf", "monsters", { position: 5, creatureType: "Humanoid (Elf)" });
  assert.equal(attack(fighter, undead, [15, 4, 4]).save_dc, null);
  const second = member("fighter-2", "heroes", {
    onHitConditionSave: structuredClone(fighter.state.template.attacks[0].onHitConditionSave),
  });
  assert.equal(attack(second, elf, [15, 4, 4]).save_dc, null);
}

{
  const ghoulTemplate = structuredClone(window.IRON_PIT_BROWSER_MONSTERS_2014["2014-ghoul"]);
  assert.ok(ghoulTemplate, "2014 Ghoul must compile into the certified browser roster");
  const claws = ghoulTemplate.attacks.find((item) => item.name === "Claws");
  assert.equal(claws.onHitConditionSave.conditionId, "paralyzed");
  assert.equal(claws.onHitConditionSave.dc, 10);
  const ghoul = { combatant_id: "ghoul", side: "monsters", position_ft: 0, state: S.buildState(ghoulTemplate) };
  const target = member("target", "heroes", { position: 5 });
  dice([15, 2, 2, 2]);
  const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(1, 1, ghoul, target, claws, 5, { spendAction: false });
  assert.equal(event.hit, true);
  assert.equal(event.save_succeeded, false);
  assert.ok(event.applied_condition_ids.includes("paralyzed"));
  assert.match(event.description, /HIT with Claws/);
  assert.match(event.description, /Paralyzed/);
}

console.log("Browser universal on-hit condition-save riders beyond Prone passed.");


{
  const fighter = member("petrifier", "heroes", {
    onHitConditionSave: { saveAbility: "constitution", dc: 12, conditionId: "petrified" },
  });
  const target = member("petrified-target", "monsters", { position: 5 });
  const event = attack(fighter, target, [15, 4, 4, 1]);
  assert.equal(event.save_succeeded, false);
  assert.ok(target.state.active_effect_ids.includes("petrified"));
  assert.equal(target.state.is_dead, true);
  assert.equal(target.state.is_alive, false);
  assert.equal(target.state.current_hp, 0);
}

{
  const fighter = member("staged-petrifier", "heroes", {
    onHitConditionSave: {
      saveAbility: "constitution", dc: 12, conditionId: "restrained",
      repeatSaveTiming: "target_turn_end", repeatSaveFailureConditionId: "petrified",
    },
  });
  const target = member("staged-target", "monsters", { position: 5 });
  const first = attack(fighter, target, [15, 4, 4, 1]);
  assert.equal(first.save_succeeded, false);
  assert.ok(target.state.active_effect_ids.includes("restrained"));
  assert.equal(target.state.is_dead, false);
  dice([1]);
  const lifecycle = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(
    2, 1, target, "target_turn_end",
  );
  assert.equal(lifecycle.events[0].save_succeeded, false);
  assert.ok(target.state.active_effect_ids.includes("petrified"));
  assert.equal(target.state.active_effect_ids.includes("restrained"), false);
  assert.equal(target.state.is_dead, true);
  assert.equal(target.state.current_hp, 0);
}
