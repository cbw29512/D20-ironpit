"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

const saveRolls = [1, 20];
let damageRollCalls = 0;
window.IRON_PIT_BROWSER_ROLLS = {
  modeFromSources: () => "normal",
  bloodiedSaveAdvantage: () => 0,
  d20: (bonus) => {
    try {
      const natural = saveRolls.shift();
      return { total: natural + bonus, mode: "normal", rolls: [natural], modifier: bonus, selected_roll: natural };
    } catch (error) {
      console.error("Failed Balor save fixture.", { error });
      throw error;
    }
  },
};
window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage: (state, amount, type) => (
    type === "fire" && state.template.damage_resistances.includes("fire")
      ? Math.floor(amount / 2) : amount
  ),
  applyDamage: (state, amount) => {
    state.current_hp = Math.max(0, state.current_hp - amount);
    return "damaged";
  },
};
window.IRON_PIT_BROWSER_GRAPPLE = { apply: () => [] };
window.IRON_PIT_BROWSER_STATE = { sizeAtMost: () => true };
window.IRON_PIT_BROWSER_CONDITION_RULES = {
  autoFailStrDex: () => false, incapacitated: () => false, has: () => false,
};
window.IRON_PIT_ACTION_ECONOMY = { available: () => true, spend: () => {} };
window.IRON_PIT_DICE = {
  rollMany: (count) => {
    try {
      damageRollCalls += 1;
      if (damageRollCalls > 2) throw new Error("Death Throes damage rolled more than once per component.");
      return Array(count).fill(6);
    } catch (error) {
      console.error("Failed Balor damage fixture.", { error });
      throw error;
    }
  },
};

load("browser-grid-geometry.js");
load("browser-mixed-save-damage.js");
load("browser-saves.js");
load("browser-death-triggers.js");

const member = (id, x, side, resistFire = false) => ({
  combatant_id: id, side, position_ft: x * 5,
  state: {
    current_hp: id === "balor" ? 0 : 200,
    temporary_hp: 0, is_alive: id !== "balor", is_dead: id === "balor",
    is_unconscious: false, is_stable: false,
    death_save_successes: 0, death_save_failures: 0,
    active_effect_ids: [], resources: {}, position: { x, y: 0 },
    template: {
      name: id, size: "medium", saving_throw_bonuses: { dexterity: 0 },
      damage_resistances: resistFire ? ["fire"] : [], traits: [],
    },
  },
});
const balor = member("balor", 0, "monsters");
balor.state.template.death_trigger_effects = [{
  id: "death-throes", name: "Death Throes", radius_ft: 30,
  save_ability: "dexterity", dc: 20,
  damage_dice_count: 9, damage_dice_size: 6, damage_bonus: 0, damage_type: "fire",
  additional_damage_components: [
    { dice_count: 9, dice_size: 6, damage_bonus: 0, damage_type: "force" },
  ],
  half_damage_on_success: true,
}];
const resistant = member("resistant", 1, "heroes", true);
const normal = member("normal", 1, "heroes");
const setup = { heroes: [resistant, normal], monsters: [balor] };

const result = window.IRON_PIT_BROWSER_DEATH_TRIGGERS.resolve(1, 1, balor, setup);
assert.equal(result.sequence, 3);
assert.equal(result.events.length, 2);
assert.equal(result.events[0].save_succeeded, false);
assert.deepEqual(result.events[0].damage_components.map((part) => part.total), [54, 54]);
assert.deepEqual(result.events[0].damage_components.map((part) => part.applied_total), [27, 54]);
assert.equal(result.events[0].damage_roll.total, 81);
assert.equal(result.events[1].save_succeeded, true);
assert.deepEqual(result.events[1].damage_components.map((part) => part.total), [27, 27]);
assert.equal(result.events[1].damage_roll.total, 54);
assert.equal(damageRollCalls, 2);

console.log("Browser Balor Death Throes shared-roll and mixed-damage parity passed.");
