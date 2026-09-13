"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-grapple.js", "browser-modifiers.js", "browser-state.js", "browser-rage.js", "browser-rolls.js",
  "browser-undead-fortitude.js", "browser-zero-hp.js", "browser-attack.js", "browser-saves.js",
  "browser-spellcasting.js", "browser-automatic-damage-spell-policy.js", "browser-automatic-damage-spell.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const P = window.IRON_PIT_BROWSER_AUTOMATIC_DAMAGE_SPELL_POLICY;
const R = window.IRON_PIT_BROWSER_AUTOMATIC_DAMAGE_SPELL;
const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];
const magicMissile = {
  id: "magic-missile", name: "Magic Missile", level: 1, actionCost: "action", range: 120,
  baseProjectiles: 3, projectilesPerSlotAbove: 1, damageDiceCountPerProjectile: 1,
  damageDiceSize: 4, damageBonusPerProjectile: 1, damageType: "force", animation: "magic-missile",
};

function dice(values) {
  const rolls = [...values];
  window.IRON_PIT_DICE = {
    roll: (sides) => {
      if (!rolls.length) throw new Error("fixed dice exhausted");
      const value = rolls.shift();
      if (value < 1 || value > sides) throw new Error(`invalid d${sides}: ${value}`);
      return value;
    },
    rollMany: (count, sides) => Array.from({ length: count }, () => window.IRON_PIT_DICE.roll(sides)),
  };
}

function member(id, side, position, caster = false) {
  const template = structuredClone(base);
  template.id = `template-${id}`; template.name = id;
  template.resources = caster ? { "spell-slot-1": 1, "spell-slot-2": 1 } : {};
  template.automatic_damage_spell_actions = caster ? [magicMissile] : [];
  return { combatant_id: id, side, position_ft: position, state: S.buildState(template) };
}

const caster = member("caster", "heroes", 0, true);
const target = member("target", "monsters", 30);
const setup = { heroes: [caster], monsters: [target] };
dice([1, 2, 4]);
const choice = P.choose(caster, setup, "1:caster");
assert.equal(choice.slotLevel, 1);
const event = R.resolve(1, 1, caster, target, magicMissile, setup, "1:caster");
assert.equal(event.attack_roll, undefined);
assert.equal(event.saving_throw_roll, undefined);
assert.equal(event.damage_roll.total, 10);
assert.equal(event.damage_components.length, 3);
assert.equal(caster.state.resources["spell-slot-1"], 0);
assert.equal(caster.state.resources["spell-slot-2"], 1);
assert.equal(caster.state.action_available, false);

console.log("Browser 2014 Magic Missile automatic-hit parity regression passed.");
