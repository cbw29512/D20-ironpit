"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(`frontend/${name}`, "utf8"),
  { filename: name },
);

window.IRON_PIT_BROWSER_STATE = {
  distance: () => 999,
};
window.IRON_PIT_BROWSER_FORMATION = {
  targetOrder: (_member, setup) => setup.monsters,
};
window.IRON_PIT_BROWSER_ROLLS = {
  modeFromSources: () => "normal",
  d20: (modifier) => ({
    notation: "1d20",
    rolls: [12],
    modifier,
    selected_roll: 12,
    mode: "normal",
    total: 12 + modifier,
  }),
};
window.IRON_PIT_BROWSER_MODIFIERS = {
  nextAttackAgainstAdvantage: () => 0,
  effectiveArmorClass: (state) => state.template.armor_class,
  applyD20Bonus: (_state, _kind, roll) => roll,
  consumeNextAttackAgainstAdvantage: () => {},
  consumeAttacksAgainstAdvantage: () => {},
  add: () => {},
};
window.IRON_PIT_BROWSER_ATTACK = {
  conditionSources: () => ({ advantage: 0, disadvantage: 0 }),
  rangedCloseThreat: () => false,
  adjustedDamage: (_state, amount) => amount,
  applyDamage: (state, amount) => {
    state.current_hp = Math.max(0, state.current_hp - amount);
    if (state.current_hp === 0) {
      state.is_alive = false;
      state.is_dead = true;
    }
    return state.is_dead ? "dead" : "damaged";
  },
};
window.IRON_PIT_BROWSER_SPELL_MODIFIERS = { build: () => ({}) };
window.IRON_PIT_BROWSER_CONDITION_RULES = { autoCritical: () => false, incapacitated: () => false };
window.IRON_PIT_BROWSER_SAP = { consume: () => 0, disadvantage: () => 0 };
window.IRON_PIT_DICE = {
  rollMany: (count) => Array.from({ length: count }, () => 4),
};

load("browser-action-economy.js");
load("browser-spellcasting.js");
load("browser-grid-geometry.js");
load("browser-spell-attack.js");
load("browser-persistent-spell-attack-support.js");
load("browser-persistent-spell-attacks.js");

const P = window.IRON_PIT_BROWSER_PERSISTENT_SPELL_ATTACKS;
const PS = window.IRON_PIT_BROWSER_PERSISTENT_SPELL_ATTACK_SUPPORT;
const spiritualWeapon = {
  id: "spiritual-weapon",
  name: "Spiritual Weapon",
  durationRounds: 10,
  moveFt: 20,
  attackReachFt: 5,
  upcastIntervalLevels: 2,
  attack: {
    id: "spiritual-weapon",
    name: "Spiritual Weapon",
    level: 2,
    actionCost: "bonus_action",
    attackKind: "melee",
    range: 60,
    attackBonus: 5,
    damageDiceCount: 1,
    damageDiceSize: 8,
    damageBonus: 3,
    damageType: "force",
    onHitModifierEffects: [],
    animation: "spiritual-weapon",
  },
};
const cleric = {
  combatant_id: "cleric",
  side: "heroes",
  position_ft: 0,
  state: {
    template: {
      name: "Seraphine",
      ruleset: "2014",
      size: "medium",
      persistent_spell_attack_actions: [spiritualWeapon],
    },
    position: { x: 0, y: 6 },
    resources: { "spell-slot-1": 4, "spell-slot-2": 2 },
    persistent_spell_attacks: [],
    spell_slot_expended_turn_key: null,
    action_available: true,
    bonus_action_available: true,
    active_modifiers: [],
  },
};
const goblin = {
  combatant_id: "goblin",
  side: "monsters",
  position_ft: 40,
  state: {
    template: { name: "Goblin", size: "medium", armor_class: 12 },
    position: { x: 8, y: 6 },
    current_hp: 20,
    temporary_hp: 0,
    death_save_successes: 0,
    death_save_failures: 0,
    concentration: null,
    active_modifiers: [],
    is_alive: true,
    is_dead: false,
  },
};
const setup = {
  heroes: [cleric],
  monsters: [goblin],
  map_definition: { width_squares: 24, height_squares: 16, cell_size_ft: 5 },
};

{
  const event = P.resolve(1, 1, cleric, setup, "1:cleric");
  assert.ok(event);
  assert.equal(event.feature_id, "spiritual-weapon");
  assert.equal(event.hit, true);
  assert.equal(event.damage_roll.total, 7);
  assert.equal(cleric.state.resources["spell-slot-2"], 1);
  assert.equal(cleric.state.spell_slot_expended_turn_key, "1:cleric");
  assert.equal(cleric.state.bonus_action_available, false);
  assert.equal(cleric.state.action_available, true);
  assert.equal(cleric.state.persistent_spell_attacks.length, 1);
  assert.equal(cleric.state.persistent_spell_attacks[0].slot_level, 2);
  assert.equal(cleric.state.persistent_spell_attacks[0].expires_round, 11);
  assert.ok(event.movement_ft <= 60);
}

{
  cleric.state.bonus_action_available = true;
  cleric.state.action_available = true;
  goblin.state.position = { x: 12, y: 6 };
  goblin.position_ft = 60;
  const slotBefore = cleric.state.resources["spell-slot-2"];
  const event = P.resolve(2, 2, cleric, setup, "2:cleric");
  assert.ok(event);
  assert.equal(event.feature_id, "spiritual-weapon");
  assert.equal(cleric.state.resources["spell-slot-2"], slotBefore);
  assert.equal(cleric.state.spell_slot_expended_turn_key, "1:cleric");
  assert.equal(cleric.state.bonus_action_available, false);
  assert.equal(cleric.state.action_available, true);
  assert.ok(event.movement_ft <= 20);
}

{
  cleric.state.bonus_action_available = true;
  cleric.state.resources["spell-slot-2"] = 0;
  const event = P.resolve(3, 11, cleric, setup, "11:cleric");
  assert.equal(event, null);
  assert.deepEqual(cleric.state.persistent_spell_attacks, []);
}

assert.deepEqual(
  PS.attackForSlot(spiritualWeapon, 4, false).damageDiceCount,
  2,
  "Spiritual Weapon adds one die for every two slot levels above 2nd.",
);

console.log("Browser persistent spell attack regressions passed.");
