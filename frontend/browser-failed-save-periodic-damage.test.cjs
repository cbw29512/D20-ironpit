"use strict";

const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

const S = window.IRON_PIT_BROWSER_STATE;
const FAILED = window.IRON_PIT_BROWSER_FAILED_SAVE_TIMED_EFFECTS;
const BURN = window.IRON_PIT_BROWSER_START_OF_TURN_TIMED_BURN;
const LIFE = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE;
const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];

function member(id, side, x) {
  const template = structuredClone(base);
  template.id = `template-${id}`;
  template.name = id;
  return {
    combatant_id: id,
    side,
    position_ft: x * 5,
    state: S.buildState(template),
  };
}

function dice(values) {
  const rolls = [...values];
  window.IRON_PIT_DICE = {
    roll(sides) {
      const value = rolls.shift();
      if (!(value >= 1 && value <= sides)) throw new Error(`invalid d${sides}: ${value}`);
      return value;
    },
    rollMany(count, sides) {
      return Array.from({ length: count }, () => this.roll(sides));
    },
  };
}

const source = member("renamed-source", "monsters", 1);
const target = member("target", "heroes", 0);
const setup = { heroes: [target], monsters: [source] };
const action = { id: "renamed-spores", dc: 14, magicalEffect: false };
const rider = {
  effectId: "poisoned",
  expiryTiming: null,
  repeatSaveAbility: "constitution",
  repeatSaveDc: 14,
  repeatSaveTiming: "target_turn_end",
  allowedRemovalActionIds: ["holy-water"],
  startOfTurnDamageDiceCount: 1,
  startOfTurnDamageDiceSize: 10,
  startOfTurnDamageType: "poison",
};

assert.equal(FAILED.apply(source, target, action, rider, 1, setup, 1), "poisoned");
const effect = target.state.timed_effects.find((item) => item.effect_id === "poisoned");
assert.ok(effect);
assert.equal(effect.expiry_timing, null);
assert.equal(effect.repeat_save_timing, "target_turn_end");
assert.equal(effect.start_of_turn_dice_count, 1);
assert.equal(effect.start_of_turn_dice_size, 10);
assert.equal(effect.start_of_turn_damage_type, "poison");
assert.deepEqual(effect.allowed_removal_action_ids, ["holy-water"]);

const hpBefore = target.state.current_hp;
dice([4]);
const tick = BURN.resolve(1, 2, target, setup);
assert.equal(tick.events.length, 1);
assert.equal(target.state.current_hp, hpBefore - 4);
assert.match(tick.events[0].description, /4 poison damage/);
assert.ok(target.state.active_effect_ids.includes("poisoned"));

dice([20]);
const recovered = LIFE.resolveTargetTiming(2, 2, target, "target_turn_end", setup);
assert.equal(recovered.events[0].save_succeeded, true);
assert.ok(!target.state.active_effect_ids.includes("poisoned"));
assert.equal(target.state.timed_effects.length, 0);

console.log("Browser failed-save periodic typed damage regression passed.");
