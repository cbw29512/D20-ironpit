"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

let damageQueue = [[3, 3], [4, 4]];
window.IRON_PIT_DICE = {
  rollMany: () => {
    try {
      const rolls = damageQueue.shift();
      if (!rolls) throw new Error("Mixed-save damage queue exhausted.");
      return rolls;
    } catch (error) {
      console.error("Failed mixed-save damage fixture roll.", { error });
      throw error;
    }
  },
};
window.IRON_PIT_BROWSER_ROLLS = {
  d20: (bonus) => ({ rolls: [1], selected_roll: 1, modifier: bonus, total: 1 + bonus, mode: "normal" }),
  modeFromSources: () => "normal",
  bloodiedSaveAdvantage: () => 0,
};
window.IRON_PIT_ACTION_ECONOMY = {
  available: () => true,
  spend: (state) => { state.action_available = false; },
};
window.IRON_PIT_BROWSER_CONDITION_RULES = {
  autoFailStrDex: () => false,
  incapacitated: () => false,
  has: () => false,
};
window.IRON_PIT_BROWSER_STATE = { sizeAtMost: () => true };
window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage: (_state, amount, type) => type === "fire" ? Math.floor(amount / 2) : amount,
  applyDamage: (state, amount) => {
    state.current_hp = Math.max(0, state.current_hp - amount);
    return null;
  },
};
window.IRON_PIT_BROWSER_GRAPPLE = {
  apply: (state, sourceId, escapeDc, range, restrains) => {
    state.grapple_sources.push({ source_id: sourceId, escape_dc: escapeDc, range_ft: range, restrains });
    return restrains ? ["grappled", "restrained"] : ["grappled"];
  },
};

load("browser-mixed-save-damage.js");
load("browser-saves.js");

const actor = {
  combatant_id: "salamander",
  state: { action_available: true, template: { name: "Salamander" } },
};
const target = {
  combatant_id: "hero",
  state: {
    current_hp: 30, temporary_hp: 0, is_alive: true, is_dead: false,
    is_unconscious: false, is_stable: false,
    death_save_successes: 0, death_save_failures: 0,
    active_effect_ids: [], grapple_sources: [],
    template: { name: "Hero", saving_throw_bonuses: { strength: 0 }, traits: [] },
  },
};
const action = {
  id: "srd-salamander-constrict", name: "Constrict", actionCost: "action",
  saveAbility: "strength", dc: 15, range: 10,
  damageDiceCount: 2, damageDiceSize: 6, damageBonus: 4, damageType: "bludgeoning",
  additionalDamageComponents: [
    { diceCount: 2, diceSize: 6, damageBonus: 0, damageType: "fire" },
  ],
  successDamage: "none", grappleEscapeDc: 14, restrainsWhileGrappled: true,
  animation: "save-effect",
};

const event = window.IRON_PIT_BROWSER_SAVES.resolveAction(
  1, 1, actor, target, action, 10,
);

assert.equal(event.save_succeeded, false);
assert.deepEqual(event.damage_components.map((part) => part.total), [10, 8]);
assert.deepEqual(event.damage_components.map((part) => part.applied_total), [10, 4]);
assert.equal(event.damage_roll.total, 14);
assert.equal(target.state.current_hp, 16);
assert.deepEqual(event.applied_condition_ids, ["grappled", "restrained"]);
assert.equal(target.state.grapple_sources[0].escape_dc, 14);

console.log("Browser mixed typed save damage and grapple parity passed.");
