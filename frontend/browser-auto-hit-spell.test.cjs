"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

load("browser-action-economy.js");
load("browser-state.js");
load("browser-spellcasting.js");

window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage: (state, amount, type) => {
    if (state.template.damage_immunities?.includes(type)) return 0;
    let value = amount;
    if (state.template.damage_resistances?.includes(type)) value = Math.floor(value / 2);
    if (state.template.damage_vulnerabilities?.includes(type)) value *= 2;
    return value;
  },
  applyDamage: (state, amount) => {
    state.current_hp = Math.max(0, state.current_hp - amount);
    if (state.current_hp === 0) {
      state.is_alive = false;
      state.is_dead = true;
    }
  },
};
window.IRON_PIT_BROWSER_OFFENSE_VALUE = {
  autoHitSpell: (target, action, projectileCount) => {
    let factor = 1;
    if (target.state.template.damage_immunities?.includes(action.damageType)) factor = 0;
    else if (target.state.template.damage_resistances?.includes(action.damageType)) factor = 0.5;
    return projectileCount * ((action.damageDiceCount || 1) * ((action.damageDiceSize || 4) + 1) / 2
      + (action.damageBonus || 0)) * factor;
  },
};

load("browser-auto-hit-spell-policy.js");
load("browser-damage-defense-rules.js");
load("browser-auto-hit-spell.js");

const S = window.IRON_PIT_BROWSER_STATE;
const P = window.IRON_PIT_BROWSER_AUTO_HIT_SPELL_POLICY;
const R = window.IRON_PIT_BROWSER_AUTO_HIT_SPELL;

function member(id, side, position, options = {}) {
  const template = {
    id: `template-${id}`, name: id, kind: options.kind || "character", ruleset: "2014",
    size: "medium", max_hp: options.hp || 40, speed_ft: 30,
    movement_modes: { walk_ft: 30, fly_ft: 0, climb_ft: 0, swim_ft: 0, burrow_ft: 0, hover: false },
    resources: options.resources || {},
    auto_hit_spell_actions: options.actions || [],
    damage_resistances: options.resistances || [],
    damage_immunities: [], damage_vulnerabilities: [],
  };
  return { combatant_id: id, side, position_ft: position, state: S.buildState(template) };
}

const magicMissile = {
  id: "magic-missile", name: "Magic Missile", level: 1, actionCost: "action", range: 120,
  projectileCount: 3, projectilesPerSlotAbove: 1,
  damageDiceCount: 1, damageDiceSize: 4, damageBonus: 1, damageType: "force",
};

{
  const caster = member("caster", "heroes", 0, {
    resources: { "spell-slot-1": 1, "spell-slot-2": 1 },
    actions: [magicMissile],
  });
  const target = member("target", "monsters", 30);
  const setup = { heroes: [caster], monsters: [target] };
  const choice = P.choose(caster, setup, "1:caster");
  assert.equal(choice.action.id, "magic-missile");
  assert.equal(choice.slotLevel, 2);
  assert.equal(choice.projectileCount, 4);

  const queue = [1, 2, 3, 4];
  window.IRON_PIT_DICE = {
    roll: () => queue.shift(),
    rollMany: (count) => Array.from({ length: count }, () => queue.shift()),
  };
  const event = R.resolve(1, 1, caster, target, setup, choice, "1:caster");
  assert.equal(event.feature_id, "magic-missile");
  assert.equal(event.damage_components.length, 4);
  assert.equal(event.damage_roll.total, 14);
  assert.equal(target.state.current_hp, 26);
  assert.equal(caster.state.resources["spell-slot-2"], 0);
  assert.equal(caster.state.action_available, false);
}

{
  const caster = member("caster-resistant", "heroes", 0, {
    resources: { "spell-slot-1": 1 },
    actions: [magicMissile],
  });
  const target = member("target-resistant", "monsters", 30, { resistances: ["force"] });
  const setup = { heroes: [caster], monsters: [target] };
  const choice = P.choose(caster, setup, "1:caster-resistant");
  assert.equal(choice.projectileCount, 3);

  const queue = [4, 4, 4];
  window.IRON_PIT_DICE = {
    roll: () => queue.shift(),
    rollMany: (count) => Array.from({ length: count }, () => queue.shift()),
  };
  const event = R.resolve(1, 1, caster, target, setup, choice, "1:caster-resistant");
  assert.deepEqual(event.damage_components.map((part) => part.applied_total), [2, 2, 2]);
  assert.equal(event.damage_roll.total, 6);
}

console.log("Browser universal auto-hit spell regression passed.");
