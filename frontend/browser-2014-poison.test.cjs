"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
load("browser-condition-immunity.js");
load("browser-timed-conditions.js");
load("browser-condition-lifecycle.js");

const T = window.IRON_PIT_BROWSER_TIMED;
const state = (ruleset) => ({
  template: { name: `${ruleset} poison target`, ruleset, condition_immunities: [] },
  active_effect_ids: [], active_buff_effect_ids: [], timed_effects: [],
});

{
  const target = state("2014");
  T.apply(target, "poisoned", "source-a", { sourceEffectId: "printed-poison" });
  const effect = target.timed_effects[0];
  assert.equal(effect.repeat_save_ability, null);
  assert.equal(effect.repeat_save_dc, null);
  assert.equal(effect.repeat_save_timing, null);
}

{
  const target = state("2014");
  T.apply(target, "poisoned", "source-a", {
    sourceEffectId: "printed-poison", appliedRound: 2,
    repeatSaveAbility: "constitution", repeatSaveDc: 12, repeatSaveTiming: "target_turn_end",
  });
  const effect = target.timed_effects[0];
  assert.equal(effect.repeat_save_ability, "constitution");
  assert.equal(effect.repeat_save_dc, 12);
  assert.equal(effect.repeat_save_timing, "target_turn_end");
}

{
  const target = state("2014");
  T.apply(target, "poisoned", "source-a", { sourceEffectId: "poison-a" });
  T.apply(target, "poisoned", "source-b", { sourceEffectId: "poison-b" });
  assert.equal(target.timed_effects.length, 2);
}

{
  const target = state("2024");
  T.apply(target, "poisoned", "source-a", { sourceEffectId: "arena-poison", appliedRound: 2 });
  const effect = target.timed_effects[0];
  assert.equal(effect.repeat_save_ability, "constitution");
  assert.equal(effect.repeat_save_dc, 10);
  assert.equal(effect.repeat_save_timing, "target_turn_start");
}

console.log("Browser 2014 Poisoned source-timing regressions passed.");
