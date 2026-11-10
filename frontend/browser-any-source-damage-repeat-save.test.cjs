"use strict";

// Verify the existing universal browser repeat-save resolver for every
// damage source, without introducing an ability-name or monster-ID branch.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE = {
  repeatSave: () => ({ succeeded: true, roll: { total: 20 }, buffs: [] }),
};
window.IRON_PIT_BROWSER_TIMED = {
  removeGroup(state, effect) {
    state.timed_effects = state.timed_effects.filter((item) => item !== effect);
    state.active_effect_ids = state.active_effect_ids.filter(
      (id) => id !== effect.effect_id,
    );
    return [effect.effect_id];
  },
};

vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-source-bound-effects.js"), "utf8"),
  { filename: "browser-source-bound-effects.js" },
);

function member(identity, side) {
  return {
    combatant_id: identity, side,
    state: {
      template: { name: identity },
      active_effect_ids: [], timed_effects: [],
      is_alive: true, is_dead: false,
    },
  };
}

function run({ ownerDealsDamage, trigger }) {
  try {
    const target = member("target", "heroes");
    const owner = member("owner", "monsters");
    const thirdParty = member("third-party", "monsters");
    const effect = {
      effect_id: "charmed",
      source_id: owner.combatant_id,
      source_effect_id: "renamed-effect",
      damage_repeat_save_trigger: trigger,
      repeat_save_ability: "wisdom",
      repeat_save_dc: 15,
      repeat_save_timing: "target_turn_end",
      repeat_save_failure_count: 0,
    };
    target.state.active_effect_ids.push("charmed");
    target.state.timed_effects.push(effect);
    const actor = ownerDealsDamage ? owner : thirdParty;
    const setup = { heroes: [target], monsters: [owner, thirdParty] };
    const result = window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS
      .resolveDamageRepeatSaves(2, 1, actor, target, setup);
    return { result, target };
  } catch (error) {
    console.error("Browser any-source repeat-save fixture failed", error);
    throw error;
  }
}

for (const ownerDealsDamage of [true, false]) {
  const { result, target } = run({
    ownerDealsDamage, trigger: "any_damage_source",
  });
  assert.equal(result.events.length, 1);
  assert.equal(result.events[0].feature_id, "renamed-effect");
  assert.equal(result.events[0].save_succeeded, true);
  assert.deepEqual(result.events[0].removed_condition_ids, ["charmed"]);
  assert.equal(result.sequence, 3);
  assert.equal(target.state.active_effect_ids.includes("charmed"), false);
}

// Existing exclusion semantics must not be broadened by the new option.
{
  const { result, target } = run({
    ownerDealsDamage: true, trigger: "other_than_effect_source",
  });
  assert.deepEqual(result.events, []);
  assert.equal(result.sequence, 2);
  assert.equal(target.state.active_effect_ids.includes("charmed"), true);
}

console.log("Browser universal any-damage-source repeat-save tests passed.");
