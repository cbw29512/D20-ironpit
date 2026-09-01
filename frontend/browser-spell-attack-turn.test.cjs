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
  "browser-offense-value.js", "browser-spellcasting.js", "browser-spell-modifiers.js",
  "browser-spell-attack-policy.js", "browser-spell-attack.js", "browser-spell-offense.js", "browser-turn.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const T = window.IRON_PIT_BROWSER_TURN;
const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];
const guidingBolt = {
  id: "guiding-bolt", name: "Guiding Bolt", level: 1, actionCost: "action", range: 120,
  attackBonus: 5, damageDiceCount: 4, damageDiceSize: 6, damageBonus: 0, damageType: "radiant",
  onHitModifierEffects: [{
    kind: "attacks-against-advantage", flatBonus: 0, diceCount: 0, diceSize: 0, damageType: null,
    consumeOnAttackAgainst: true, expiresAfterSourceTurns: 1,
  }], animation: "guiding-bolt",
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

function member(id, side, position, options = {}) {
  const template = structuredClone(base);
  template.id = `template-${id}`; template.name = id; template.armor_class = options.armorClass ?? 10;
  template.resources = options.caster ? { "spell-slot-1": 1 } : {};
  template.spell_attack_actions = options.caster ? [guidingBolt] : [];
  template.spell_save_actions = [];
  return { combatant_id: id, side, position_ft: position, state: S.buildState(template) };
}

const caster = member("caster", "heroes", 0, { caster: true });
const target = member("target", "monsters", 30);
const setup = { heroes: [caster], monsters: [target] };
dice([15, 6, 5, 4, 3]);
const turn = T.resolveTurn(1, 1, caster, setup);

assert.equal(turn.sequence, 2);
assert.equal(turn.events.length, 1);
assert.equal(turn.events[0].feature_id, "guiding-bolt");
assert.equal(turn.events[0].hit, true);
assert.equal(turn.events[0].damage_roll.total, 18);
assert.equal(caster.state.resources["spell-slot-1"], 0);
assert.equal(caster.state.action_available, false);
assert.equal(target.state.active_modifiers.length, 1);

console.log("Browser live-turn unified spell offense dispatch regression passed.");
