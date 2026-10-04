"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

window.IRON_PIT_ACTION_ECONOMY = {
  available: () => true,
  spend: (state, cost) => {
    if (cost === "bonus_action") state.bonus_action_available = false;
    else state.action_available = false;
  },
};
window.IRON_PIT_BROWSER_SPELLCASTING = {
  slotSpellAvailable: () => true,
  markSlotSpellCast: () => {},
};
window.IRON_PIT_BROWSER_STATE = {
  effectiveMaxHp: (state) => state.template.max_hp + (state.max_hp_bonus || 0),
  distance: (a, b) => Math.abs((a.state.position?.x || 0) - (b.state.position?.x || 0)) * 5,
};
window.IRON_PIT_DICE = { roll: () => 8 };
window.IRON_PIT_BROWSER_CONDITION_RULES = {
  has: (state, id) => (state.active_effect_ids || []).includes(id),
  incapacitated: (state) => state.is_unconscious || (state.active_effect_ids || []).includes("incapacitated"),
};

load("browser-modifier-validation.js");
load("browser-modifiers.js");
load("browser-zero-hp-replacement.js");
load("browser-zero-hp.js");
load("browser-healing-policy.js");
load("browser-healing-resolution.js");
load("browser-healing.js");
load("browser-group-healing.js");
load("browser-friendly-save-auras.js");

function combatant(id, side, hp, maxHp, x = 0) {
  return {
    combatant_id: id,
    side,
    position_ft: x * 5,
    state: {
      template: {
        id, name: id, max_hp: maxHp, creature_type: "Humanoid", traits: [],
        healingActions: [], timed_self_buff_actions: [],
      },
      resources: { "spell-slot-6": 1, "spell-slot-9": 1 },
      current_hp: hp,
      max_hp_bonus: 0,
      is_alive: true,
      is_dead: false,
      is_unconscious: hp === 0,
      is_stable: false,
      death_save_successes: 0,
      death_save_failures: 0,
      action_available: true,
      bonus_action_available: true,
      timed_effects: [],
      active_effect_ids: [],
      active_modifiers: [],
      position: { x, y: 0 },
    },
  };
}

{
  const healer = combatant("cleric", "heroes", 40, 40);
  const ally = combatant("ally", "heroes", 0, 20, 1);
  healer.state.template.healingActions = [
    {
      id: "healing-word", name: "Healing Word", actionCost: "bonus_action", range: 60,
      targetMode: "self_or_ally", maxTargets: 1, diceCount: 2, diceSize: 4, healingBonus: 5,
      resourceId: "spell-slot-1", resourceCost: 1,
    },
    {
      id: "spare-the-dying", name: "Spare the Dying", actionCost: "action", range: 30,
      targetMode: "self_or_ally", maxTargets: 1, diceCount: 0, diceSize: 6, healingBonus: 0,
      stabilizeAtZero: true,
    },
  ];
  healer.state.resources["spell-slot-1"] = 1;
  const setup = { heroes: [healer, ally], monsters: [] };
  const withWord = window.IRON_PIT_BROWSER_HEALING.chooseAction(healer, setup, "1:cleric");
  assert.equal(withWord.action.id, "healing-word");
  healer.state.resources["spell-slot-1"] = 0;
  const spareOnly = window.IRON_PIT_BROWSER_HEALING.chooseAction(healer, setup, "1:cleric");
  assert.equal(spareOnly.action.id, "spare-the-dying");
  const event = window.IRON_PIT_BROWSER_HEALING.resolve(1, 1, healer, ally, spareOnly.action, "1:cleric");
  assert.equal(ally.state.is_stable, true);
  assert.equal(ally.state.current_hp, 0);
  assert.equal(event.healing_roll.notation, "stabilize");
}

{
  const healer = combatant("cleric", "heroes", 40, 40);
  const first = combatant("first", "heroes", 0, 12, 1);
  const second = combatant("second", "heroes", 2, 12, 1);
  const action = {
    id: "mass-heal", name: "Mass Heal", actionCost: "action", range: 60,
    targetMode: "self_or_ally", maxTargets: 6, diceCount: 0, diceSize: 6, healingBonus: 11,
    sharedHealingPool: 700, resourceId: "spell-slot-9", resourceCost: 1,
    removableConditions: [],
  };
  healer.state.template.healingActions = [action];
  const setup = { heroes: [healer, first, second], monsters: [] };
  const targets = window.IRON_PIT_BROWSER_HEALING.groupTargets(healer, setup, action, "1:cleric");
  const result = window.IRON_PIT_BROWSER_HEALING.resolveGroup(1, 1, healer, targets, action, "1:cleric", setup);
  assert.equal(first.state.current_hp, 12);
  assert.equal(second.state.current_hp, 12);
  assert.equal(result.events[0].healing_roll.total, 23);
}

{
  const source = combatant("cleric", "heroes", 40, 40);
  const ally = combatant("ally", "heroes", 20, 20, 1);
  source.state.timed_effects.push({
    source_id: "cleric", source_effect_id: "holy-aura", effect_id: "holy-aura",
  });
  source.state.template.timed_self_buff_actions = [{
    id: "holy-aura",
    name: "Holy Aura",
    friendlySaveAdvantageAura: {
      radius_ft: 30, all_saves: true, attacks_against_disadvantage: true,
      melee_hit_save_retaliation: {
        attacker_creature_types: ["fiend", "undead"],
        save_ability: "constitution", save_dc: 18, condition_id: "blinded",
        expiry_timing: "target_turn_end", duration_rounds: 1,
      },
    },
  }];
  window.IRON_PIT_BROWSER_FRIENDLY_SAVE_AURAS.sync({ heroes: [source, ally], monsters: [] });
  assert.ok(ally.state.active_modifiers.some((item) => item.kind === "saving-throw-advantage" && !(item.required_effect_tags || []).length));
  assert.ok(ally.state.active_modifiers.some((item) => item.kind === "attacks-against-disadvantage"));
}

{
  const target = {
    template: { id: "target", name: "Target", kind: "character", max_hp: 20, traits: [], condition_immunities: [] },
    current_hp: 5, max_hp_bonus: 0, temporary_hp: 0,
    is_alive: true, is_dead: false, is_unconscious: false, is_stable: false,
    death_save_successes: 0, death_save_failures: 0,
    active_effect_ids: [], active_buff_effect_ids: ["death-ward"],
    active_modifiers: [{
      id: "caster:death-ward:target:0", source_id: "caster", source_effect_id: "death-ward",
      source_name: "Death Ward", source_is_magical: true, kind: "zero-hp-replacement",
      replacement_hp: 1, prevents_instant_death: true,
    }],
    pending_zero_hp_replacement_logs: [], concentration: null,
  };
  assert.equal(window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(target, 20), "zero_hp_replacement");
  assert.equal(target.current_hp, 1);
}

console.log("2024 leftover Cleric combat spells browser parity passed.");
