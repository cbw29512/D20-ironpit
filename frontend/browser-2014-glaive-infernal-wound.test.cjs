"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
let saves = 0;
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_SAVING_THROWS = {
  resolveSavingThrow: () => {
    saves += 1;
    return { succeeded: false, roll: { selected_roll: 1, total: 1 } };
  },
};
window.IRON_PIT_BROWSER_STATE = { effectiveMaxHp: (state) => state.template.max_hp };
window.IRON_PIT_BROWSER_HEALING_POLICY = {
  swarm: () => false, slotHeal: () => false,
  targetAllowed: () => true, resourceAvailable: () => true,
  healingMaximized: () => false,
};
window.IRON_PIT_ACTION_ECONOMY = { available: () => true, spend: () => {} };
window.IRON_PIT_DICE = { roll: () => 3 };
window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES = {
  resolveDamage: () => { throw new Error("HP loss cannot invoke typed damage"); },
};
window.IRON_PIT_BROWSER_ATTACK = {
  applyDamage: () => { throw new Error("HP loss cannot invoke damage"); },
};
window.IRON_PIT_BROWSER_ZERO_HP = {
  reduceToZero: (state) => { state.current_hp = 0; state.is_unconscious = true; },
};
load("browser-timed-conditions.js");
load("browser-on-hit-condition-save.js");
load("browser-healing-resolution.js");
load("browser-healing.js");
load("browser-start-of-turn-timed-burn.js");
const wound = window.IRON_PIT_BROWSER_ON_HIT_CONDITION_SAVE.resolveOngoingHpLoss;
const timed = window.IRON_PIT_BROWSER_TIMED;
const healing = window.IRON_PIT_BROWSER_HEALING;
const burn = window.IRON_PIT_BROWSER_START_OF_TURN_TIMED_BURN;
const attack = { name: "Glaive", onHitOngoingHpLoss: {
  effectId: "infernal-wound", sourceName: "Infernal Wound",
  saveAbility: "constitution", dc: 12, diceCount: 1, diceSize: 10,
  excludedCreatureTypes: ["undead", "construct"],
  stacksOnReapply: true, endsOnMagicalHealing: true,
}};
const target = {
  combatant_id: "target", side: "heroes",
  state: {
    template: { name: "Target", max_hp: 100, creature_type: "humanoid" },
    current_hp: 70, temporary_hp: 30, timed_effects: [],
    active_effect_ids: [], active_modifiers: [],
    is_alive: true, is_dead: false, is_unconscious: false,
  },
};
const devil1 = { combatant_id: "devil-one" };
const devil2 = { combatant_id: "devil-two" };
assert.equal(wound(target, attack, {}, 1, null, devil1).saveSucceeded, false);
assert.equal(saves, 1);
assert.equal(wound(target, attack, {}, 1, null, devil1).saveSucceeded, null);
assert.equal(saves, 1, "existing source wound stacks without a new saving throw");
assert.equal(target.state.timed_effects[0].start_of_turn_hp_loss_dice_count, 2);
wound(target, attack, {}, 1, null, devil2);
assert.equal(saves, 2);
assert.equal(target.state.timed_effects.length, 2, "second devil owns separate wound");
const tick = burn.resolve(1, 2, target, { heroes: [target], monsters: [] });
assert.equal(target.state.current_hp, 61);
assert.equal(target.state.temporary_hp, 30);
assert.equal(tick.events.length, 2);
timed.apply(target.state, "poisoned", "devil-beard", {
  sourceEffectId: "Beard", cannotRegainHitPoints: true,
  useDefaultPoisonRecovery: false,
});
const healer = { combatant_id: "target", state: target.state };
const action = {
  id: "magical-heal", name: "Magical Healing", actionCost: "action",
  healingBonus: 9, magicalHealing: true, grantsTemporaryHp: false,
};
const event = healing.resolve(3, 2, healer, target, action);
assert.equal(event.hp_after, 61, "Beard still suppresses actual hit point recovery");
assert.ok(target.state.active_effect_ids.includes("poisoned"));
assert.equal(target.state.timed_effects.filter((e) => e.effect_id === "infernal-wound").length, 0);
console.log("Glaive wound stacking, source ownership, raw HP loss, and magical-healing closure passed.");
