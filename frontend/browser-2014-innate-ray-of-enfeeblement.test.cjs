"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
for (const file of [
  "browser-damage-defense-rules.js", "browser-heroes.js", "browser-condition-immunity.js",
  "browser-condition-rules.js", "browser-action-economy.js", "browser-grapple.js",
  "browser-timed-conditions.js", "browser-weapon-mastery.js", "browser-tactical-master.js",
  "browser-barbarian2.js", "browser-modifier-validation.js", "browser-modifiers.js",
  "browser-state.js", "browser-rage.js", "browser-rolls.js", "browser-heroic-inspiration.js",
  "browser-undead-fortitude.js", "browser-zero-hp.js", "browser-ability-hooks.js",
  "browser-attack-outcome.js", "browser-attack.js",
  "browser-concentration.js", "browser-spellcasting.js", "browser-spell-modifiers.js",
  "browser-spell-attack.js", "browser-condition-lifecycle.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
window.IRON_PIT_BROWSER_SAVES = {
  resolveSavingThrow: (_state, ability, dc) => ({
    roll: { notation: "1d20+0", rolls: [window.IRON_PIT_DICE.roll(20)], modifier: 0,
      selected_roll: 20, mode: "normal", total: 20 },
    ability, dc, succeeded: true,
  }),
};
const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];
const spell = {
  id: "ray-of-enfeeblement", name: "Ray of Enfeeblement", level: 2,
  actionCost: "action", attackKind: "ranged", range: 60, attackBonus: 6,
  damageDiceCount: 0, damageDiceSize: 6, damageBonus: 0, damageType: null,
  concentration: true, durationMinutes: 1,
  onHitModifierEffects: [{
    kind: "weapon-attack-damage-multiplier", multiplier: 0.5,
    requiredAttackAbility: "strength",
  }],
  onHitTimedEffects: [{
    effectId: "ray-of-enfeeblement", durationRounds: 10,
    expiryTiming: "source_turn_start", sourceIsMagical: true,
    repeatSaveAbility: "constitution", repeatSaveDc: 14,
    repeatSaveTiming: "target_turn_end",
  }],
};
const grant = {
  source_id: spell.id, source_name: spell.name, spell_id: spell.id,
  cast_level: 2, resource_id: spell.id, resource_cost: 1,
};
function member(id, side, position) {
  const template = structuredClone(base);
  template.id = id; template.name = id; template.armor_class = 10;
  template.resources = side === "monsters" ? { [spell.id]: 2 } : {};
  return { combatant_id: id, side, position_ft: position, state: S.buildState(template) };
}
function dice(values) {
  const rolls = [...values];
  window.IRON_PIT_DICE = {
    roll: () => rolls.shift(),
    rollMany: (count) => Array.from({ length: count }, () => rolls.shift()),
  };
}

const caster = member("night-hag", "monsters", 0);
const target = member("target", "heroes", 30);
const setup = { heroes: [target], monsters: [caster] };
const immutable = JSON.stringify(spell);
dice([15]);
const event = window.IRON_PIT_BROWSER_SPELL_ATTACK.resolve(
  1, 1, caster, target, spell, setup, "1:night-hag",
  { castSlotLevel: 2, alternateCast: grant },
);
assert.equal(event.hit, true);
assert.equal(event.damage_roll, null);
assert.equal(event.resource_remaining, 1);
assert.equal(caster.state.concentration.effect_id, spell.id);
assert.equal(target.state.active_modifiers[0].multiplier, 0.5);
assert.equal(target.state.timed_effects[0].repeat_save_dc, 14);
assert.equal(JSON.stringify(spell), immutable);

dice([20]);
const lifecycle = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(
  2, 1, target, "target_turn_end", setup,
);
assert.equal(lifecycle.events[0].save_succeeded, true);
assert.equal(caster.state.concentration, null);
assert.deepEqual(target.state.active_modifiers, []);
assert.deepEqual(target.state.timed_effects, []);

console.log("2014 innate Ray of Enfeeblement browser parity passed.");
