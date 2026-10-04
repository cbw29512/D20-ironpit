"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

window.IRON_PIT_DICE = {
  rolls: [],
  roll(sides) {
    if (!this.rolls.length) throw new Error("No queued d" + sides + " roll");
    return this.rolls.shift();
  },
};
window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage(_state, total) { return total; },
  applyDamage(state, applied) { state.current_hp -= applied; return applied; },
};
window.IRON_PIT_BROWSER_TIMED = {
  removeEffect(state, effect) {
    state.timed_effects = state.timed_effects.filter((item) => item !== effect);
    state.active_effect_ids = (state.active_effect_ids || [])
      .filter((id) => state.timed_effects.some((item) => item.effect_id === id));
  },
};
window.IRON_PIT_BROWSER_CONCENTRATION = { end() { return false; } };
window.IRON_PIT_BROWSER_SAVING_THROWS = {
  resolveSavingThrow(state, _ability, dc) {
    const roll = window.IRON_PIT_DICE.roll(20);
    return { succeeded: roll >= dc, roll };
  },
};

load("browser-start-of-turn-timed-burn.js");

function member() {
  return {
    combatant_id: "enemy",
    state: {
      template: { name: "Commoner", saving_throw_bonuses: { constitution: 0 } },
      current_hp: 20,
      timed_effects: [{
        effect_id: "searing-smite",
        source_id: "aurelia",
        source_effect_id: "searing-smite",
        start_of_turn_dice_count: 1,
        start_of_turn_dice_size: 6,
        start_of_turn_damage_type: "fire",
        start_of_turn_save_ability: "constitution",
        start_of_turn_save_dc: 13,
        start_of_turn_save_ends: true,
      }],
      active_effect_ids: ["searing-smite"],
      concentration: null,
    },
  };
}

const first = member();
const setup = { heroes: [{ combatant_id: "aurelia", state: { concentration: null, timed_effects: [] } }], monsters: [first] };
window.IRON_PIT_DICE.rolls = [6, 1];
const fail = window.IRON_PIT_BROWSER_START_OF_TURN_TIMED_BURN.resolve(1, 2, first, setup);
assert.equal(first.state.current_hp, 14);
assert.equal(fail.events.length, 1);
assert.ok(first.state.timed_effects.some((item) => item.effect_id === "searing-smite"));

window.IRON_PIT_DICE.rolls = [4, 20];
window.IRON_PIT_BROWSER_START_OF_TURN_TIMED_BURN.resolve(2, 3, first, setup);
assert.equal(first.state.current_hp, 10);
assert.equal(first.state.timed_effects.length, 0);
console.log("browser start-of-turn timed burn tests passed");
