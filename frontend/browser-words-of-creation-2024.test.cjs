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
  available: (state, cost) => cost === "reaction" ? state.reaction_available : state.action_available,
  spend: (state, cost) => {
    if (cost === "reaction") state.reaction_available = false;
    else if (cost === "bonus_action") state.bonus_action_available = false;
    else state.action_available = false;
  },
};
window.IRON_PIT_BROWSER_SPELLCASTING = {
  slotSpellAvailable: () => true,
  markSlotSpellCast: () => {},
};
window.IRON_PIT_BROWSER_STATE = {
  effectiveMaxHp: (state) => state.template.max_hp,
};
window.IRON_PIT_BROWSER_SPELL_AREA = { bestFriendlyPlacement: () => null };
window.IRON_PIT_DICE = {
  roll: () => 1,
  rollMany: (count) => Array(count).fill(1),
};

for (const file of [
  "browser-condition-removal.js",
  "browser-healing-policy.js",
  "browser-healing-resolution.js",
  "browser-healing.js",
  "browser-group-healing.js",
]) load(file);

function healingMember(id, position, hp = 20) {
  return {
    combatant_id: id,
    side: "heroes",
    position_ft: position,
    state: {
      template: { id, name: id, max_hp: 20, creature_type: "Humanoid", traits: [] },
      resources: {},
      current_hp: hp,
      is_alive: true,
      is_dead: false,
      is_unconscious: false,
      is_stable: false,
      death_save_successes: 0,
      death_save_failures: 0,
      action_available: true,
      bonus_action_available: true,
      reaction_available: true,
      active_effect_ids: [],
      timed_effects: [],
      grapple_sources: [],
    },
  };
}

{
  const healer = healingMember("lyra", 0, 20);
  const first = healingMember("first", 10, 1);
  const second = healingMember("second", 20, 2);
  healer.state.resources["spell-slot-9"] = 1;
  first.state.active_effect_ids.push("charmed", "prone");
  second.state.active_effect_ids.push("poisoned");
  const setup = { heroes: [healer, first, second], monsters: [] };
  const action = {
    id: "power-word-heal", name: "Power Word Heal", actionCost: "action",
    range: 60, targetMode: "any", maxTargets: 2, restoreToEffectiveMax: true,
    resourceId: "spell-slot-9", resourceCost: 1,
    removableConditions: ["charmed", "frightened", "paralyzed", "poisoned", "stunned"],
    proneReactionStand: true, secondaryTargetWithinFt: 10,
  };

  const result = window.IRON_PIT_BROWSER_HEALING.resolveGroup(
    1, 1, healer, [first, second], action, "1:lyra", setup,
  );
  assert.equal(result.events.length, 2);
  assert.equal(healer.state.resources["spell-slot-9"], 0);
  assert.equal(healer.state.action_available, false);
  assert.equal(first.state.current_hp, 20);
  assert.equal(second.state.current_hp, 20);
  assert.deepEqual(first.state.active_effect_ids, []);
  assert.deepEqual(second.state.active_effect_ids, []);
  assert.equal(first.state.reaction_available, false);
  assert.deepEqual(result.events[0].removed_condition_ids, ["charmed", "prone"]);
  assert.deepEqual(result.events[1].removed_condition_ids, ["poisoned"]);

  healer.state.resources["spell-slot-9"] = 1;
  healer.state.action_available = true;
  first.state.current_hp = 1;
  second.state.current_hp = 1;
  second.position_ft = 25;
  assert.throws(
    () => window.IRON_PIT_BROWSER_HEALING.resolveGroup(
      3, 1, healer, [first, second], action, "2:lyra", setup,
    ),
    /linked-target distance|legal healing area/,
  );
}

window.IRON_PIT_BROWSER_FORMATION = {
  saveDistance: (a, b) => Math.abs(a.position_ft - b.position_ft),
  targetOrder: (member, setup) => (member.side === "heroes" ? setup.monsters : setup.heroes),
};
window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES = { adjustedDamage: (_state, amount) => amount };
window.IRON_PIT_BROWSER_ZERO_HP = {
  applyDamage: (state, amount) => {
    state.current_hp = Math.max(0, state.current_hp - amount);
    if (state.current_hp === 0) {
      state.is_alive = false;
      state.is_dead = true;
    }
  },
  applyInstantDeath: (state) => {
    state.current_hp = 0;
    state.is_alive = false;
    state.is_dead = true;
    return "dead";
  },
};
window.IRON_PIT_BROWSER_ZERO_HP_REPLACEMENT = { consumeLog: () => "" };
load("browser-hp-threshold-instant-death.js");

function thresholdMember(id, side, position, hp) {
  return {
    combatant_id: id,
    side,
    position_ft: position,
    state: {
      template: {
        id, name: id, max_hp: 200,
        hp_threshold_instant_death_actions: [],
      },
      resources: {},
      current_hp: hp,
      is_alive: true,
      is_dead: false,
      action_available: true,
    },
  };
}

{
  const lyra = thresholdMember("lyra", "heroes", 0, 100);
  const first = thresholdMember("first", "monsters", 30, 100);
  const second = thresholdMember("second", "monsters", 40, 150);
  const setup = { heroes: [lyra], monsters: [first, second] };
  const action = {
    id: "power-word-kill", name: "Power Word Kill", actionCost: "action",
    range: 60, maxCurrentHp: 100,
    fallbackDamageDiceCount: 12, fallbackDamageDiceSize: 12,
    fallbackDamageBonus: 0, fallbackDamageType: "psychic",
    resourceId: "spell-slot-9", resourceCost: 1,
    maxTargets: 2, secondaryTargetWithinFt: 10,
  };
  lyra.state.template.hp_threshold_instant_death_actions = [action];
  lyra.state.resources["spell-slot-9"] = 1;

  const selected = window.IRON_PIT_BROWSER_HP_THRESHOLD_INSTANT_DEATH.choose(lyra, setup);
  assert.deepEqual(selected.targets.map((item) => item.combatant_id), ["first", "second"]);
  const events = window.IRON_PIT_BROWSER_HP_THRESHOLD_INSTANT_DEATH.resolveGroup(
    1, 1, lyra, selected.targets, action, setup,
  );
  assert.equal(events.length, 2);
  assert.equal(lyra.state.resources["spell-slot-9"], 0);
  assert.equal(lyra.state.action_available, false);
  assert.equal(first.state.is_dead, true);
  assert.equal(second.state.current_hp, 138);
}

console.log("2024 Words of Creation browser regressions passed.");
