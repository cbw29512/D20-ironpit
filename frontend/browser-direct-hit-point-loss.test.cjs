"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");
global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
window.IRON_PIT_DICE = { roll: () => 4 };
window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES = {
  resolveDamage: () => { throw new Error("Raw HP loss must not use typed damage"); },
};
window.IRON_PIT_BROWSER_ATTACK = {
  applyDamage: () => { throw new Error("Raw HP loss must not trigger a damage event"); },
};
let transitions = 0;
window.IRON_PIT_BROWSER_ZERO_HP = {
  reduceToZero: (state) => {
    transitions += 1; state.current_hp = 0; state.is_unconscious = true;
    return "unconscious";
  },
};
load("browser-start-of-turn-timed-burn.js");
const member = (hp, stacks) => ({
  combatant_id: "hero", state: {
    template: { name: "Hero" }, current_hp: hp, temporary_hp: 40,
    timed_effects: [{
      effect_id: "infernal-wound", source_id: "devil-one",
      source_effect_id: "Glaive", start_of_turn_hp_loss_dice_count: stacks,
      start_of_turn_hp_loss_dice_size: 10,
    }],
  },
});
{
  const hero = member(15, 2);
  const result = window.IRON_PIT_BROWSER_START_OF_TURN_TIMED_BURN.resolve(
    1, 2, hero, { heroes: [hero], monsters: [] },
  );
  assert.equal(hero.state.current_hp, 7);
  assert.equal(hero.state.temporary_hp, 40);
  assert.equal(result.events.length, 1);
  assert.equal(result.events[0].hp_before, 15);
  assert.equal(result.events[0].hp_after, 7);
  assert.equal(transitions, 0);
}
{
  const hero = member(5, 2);
  window.IRON_PIT_BROWSER_START_OF_TURN_TIMED_BURN.resolve(
    1, 3, hero, { heroes: [hero], monsters: [] },
  );
  assert.equal(transitions, 1);
  assert.equal(hero.state.current_hp, 0);
  assert.equal(hero.state.temporary_hp, 40);
}
console.log("Direct start-turn HP loss bypasses typed damage, Temp HP and invokes zero-HP transition.");
