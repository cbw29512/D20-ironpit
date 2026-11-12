"use strict";

// Real generated source card + shared browser timed-buff and modifier engines.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (file) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, file), "utf8"), { filename: file },
);

try {
  for (const file of [
    "browser-monsters-2014.js", "browser-modifier-validation.js",
    "browser-modifiers.js", "browser-action-economy.js",
    "browser-timed-conditions.js", "browser-timed-condition-lifecycle.js",
    "browser-concentration.js", "browser-spell-modifiers.js",
    "browser-timed-self-buff-policy.js", "browser-timed-self-buffs.js",
  ]) load(file);

  const card = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-druid"];
  assert.ok(card, "The real 2014 Druid must pass source admission before browser play.");
  assert.equal(card.ruleset, "2014");
  const spells = new Set([
    ...(card.spell_save_actions || []),
    ...(card.spell_attack_actions || []),
    ...(card.defensive_spell_actions || []),
  ].map((spell) => spell.id));
  for (const id of ["entangle", "thunderwave", "produce-flame", "longstrider", "barkskin"]) {
    assert.ok(spells.has(id), `Druid lost printed ${id}.`);
  }
  const buff = card.timed_self_buff_actions.find((action) => action.id === "shillelagh");
  assert.ok(buff);
  assert.equal(buff.actionCost, "bonus_action");
  assert.equal(buff.durationRounds, 10);
  assert.equal(Boolean(buff.concentration), false);
  assert.equal(buff.modifierEffects.length, 4);

  const staff = card.attacks.find((attack) => attack.id === "2014-druid-quarterstaff");
  assert.ok(staff);
  assert.ok(!card.attacks.some((attack) => attack.id.includes("quarterstaff-shillelagh")));
  assert.equal(staff.conditionalDamage.trigger, "attacker_active_effect");
  assert.equal(staff.conditionalDamage.requiredEffectId, "shillelagh");
  assert.equal(staff.conditionalDamage.mode, "replace_weapon");
  assert.equal(staff.conditionalDamage.diceCount, 1);
  assert.equal(staff.conditionalDamage.diceSize, 8);
  assert.equal(staff.conditionalDamage.damageBonus, 2);

  const state = {
    template: card, resources: { ...card.resources }, current_hp: card.max_hp,
    is_alive: true, is_dead: false, is_unconscious: false,
    action_available: true, bonus_action_available: true, reaction_available: true,
    active_effect_ids: [], active_modifiers: [], timed_effects: [], concentration: null,
    voluntary_turn_activity: null, delayed_resource_refills: [],
  };
  const caster = { combatant_id: "caster", side: "monsters", state };
  const modifiers = window.IRON_PIT_BROWSER_MODIFIERS;
  assert.equal(modifiers.attackRollFlat(state, staff.weaponId || staff.id), 0);
  assert.equal(modifiers.damageSourceQualifiers(state, staff).has("magical"), false);

  const event = window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS.resolve(
    1, 1, caster, buff, { affectedStates: [state] },
  );
  assert.equal(event.feature_id, "shillelagh");
  assert.equal(state.bonus_action_available, false);
  assert.equal(state.action_available, true);
  assert.equal(state.active_effect_ids.includes("shillelagh"), true);
  assert.equal(modifiers.attackRollFlat(state, staff.weaponId || staff.id), 2);
  assert.equal(modifiers.damageSourceQualifiers(state, staff).has("magical"), true);

  const timer = state.timed_effects.find((effect) => effect.source_effect_id === "shillelagh");
  assert.ok(timer);
  window.IRON_PIT_BROWSER_TIMED.removeGroup(state, timer);
  assert.equal(modifiers.attackRollFlat(state, staff.weaponId || staff.id), 0);
  assert.equal(modifiers.damageSourceQualifiers(state, staff).has("magical"), false);
  console.log("2014 Druid Shillelagh browser source, activation and expiry passed.");
} catch (error) {
  console.error("2014 Druid browser source/buff parity failed", error);
  throw error;
}
