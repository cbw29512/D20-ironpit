"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;

function load(name) {
  try {
    vm.runInThisContext(
      fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
    );
  } catch (error) {
    console.error("Failed loading wound regression dependency", { name, error });
    throw error;
  }
}

let saveCount = 0;
let shouldSave = false;
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_SAVING_THROWS = {
  resolveSavingThrow() {
    saveCount += 1;
    return { succeeded: shouldSave, roll: { selected_roll: shouldSave ? 20 : 1, total: shouldSave ? 20 : 1 } };
  },
};
window.IRON_PIT_BROWSER_STATE = { effectiveMaxHp: (state) => state.template.max_hp };
window.IRON_PIT_DICE = { roll: () => 3 };
window.IRON_PIT_BROWSER_ZERO_HP = { reduceToZero: (state) => {
  state.current_hp = 0; state.is_unconscious = true;
} };
load("browser-start-of-turn-timed-burn.js");
load("browser-on-hit-condition-save.js");
load("browser-timed-conditions.js");

const wound = window.IRON_PIT_BROWSER_ON_HIT_CONDITION_SAVE.resolveOngoingHpLoss;
const burn = window.IRON_PIT_BROWSER_START_OF_TURN_TIMED_BURN;
const timed = window.IRON_PIT_BROWSER_TIMED;
const attack = { id: "glaive", name: "Glaive", onHitOngoingHpLoss: {
  effectId: "infernal-wound", sourceName: "Infernal Wound",
  saveAbility: "constitution", dc: 12, diceCount: 1, diceSize: 10,
  excludedCreatureTypes: ["undead", "construct"],
  stacksOnReapply: true, endsOnMagicalHealing: true,
} };

function targetFor(kind = "humanoid") {
  return {
    combatant_id: "target", side: "heroes",
    state: {
      template: { name: "Target", max_hp: 100, creature_type: kind },
      current_hp: 70, temporary_hp: 20, timed_effects: [],
      active_effect_ids: [], active_modifiers: [],
      is_alive: true, is_dead: false, is_unconscious: false,
    },
  };
}

try {
  const target = targetFor();
  const devil1 = { combatant_id: "devil-one" };
  const devil2 = { combatant_id: "devil-two" };
  assert.equal(wound(target, attack, null, 1, null, devil1).saveSucceeded, false);
  assert.equal(saveCount, 1);
  assert.equal(wound(target, attack, null, 1, null, devil1).saveSucceeded, null);
  assert.equal(saveCount, 1, "A repeat hit from this devil does not force another save.");
  assert.equal(target.state.timed_effects[0].start_of_turn_hp_loss_dice_count, 2);
  wound(target, attack, null, 1, null, devil2);
  assert.equal(saveCount, 2);
  assert.equal(target.state.timed_effects.length, 2);
  const tick = burn.resolve(1, 2, target, { heroes: [target], monsters: [] });
  assert.equal(tick.events.length, 2);
  assert.equal(target.state.current_hp, 61);
  assert.equal(target.state.temporary_hp, 20);
  target.state.timed_effects.push({
    effect_id: "poisoned", source_id: "beard", source_effect_id: "Beard",
    cannot_regain_hit_points: true,
  });
  target.state.active_effect_ids.push("poisoned");
  assert.deepEqual(timed.removeOnMagicalHealing(target.state), ["infernal-wound"]);
  assert.equal(target.state.timed_effects.length, 1);
  assert.equal(target.state.timed_effects[0].effect_id, "poisoned");

  for (const kind of ["undead", "construct"]) {
    const immune = targetFor(kind);
    assert.equal(wound(immune, attack, null, 1, null, devil1), null);
    assert.equal(immune.state.timed_effects.length, 0);
  }
  shouldSave = true;
  const saved = targetFor();
  assert.equal(wound(saved, attack, null, 1, null, devil1).saveSucceeded, true);
  assert.equal(saved.state.timed_effects.length, 0);
  console.log("Browser ongoing Glaive wound source, save, stacks and magical-heal removal passed.");
} catch (error) {
  console.error("2014 Glaive Infernal Wound regression failed", error);
  throw error;
}
