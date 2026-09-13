"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS = { endDamageSensitive: () => {} };
window.IRON_PIT_BROWSER_STATE = { effectiveMaxHp: (state) => state.template.max_hp };
window.IRON_PIT_BROWSER_CONCENTRATION = null;
window.IRON_PIT_BROWSER_UNDEAD_FORTITUDE = null;
load("browser-zero-hp.js");

function state(threshold) {
  return {
    current_hp: 5, temporary_hp: 0, is_alive: true, is_dead: false,
    is_unconscious: false, is_stable: false, death_save_failures: 0,
    active_effect_ids: [], resources: { relentless: 1 }, concentration: null,
    template: {
      name: "Boar", kind: "monster", max_hp: 11, traits: [],
      zeroHpPrevention: { resourceId: "relentless", maxTriggerDamage: threshold, resultingHp: 1 },
    },
  };
}

let boar = state(7);
assert.equal(window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(boar, 7), "zero_hp_prevention");
assert.equal(boar.current_hp, 1);
assert.equal(boar.resources.relentless, 0);
assert.equal(window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(boar, 7), "dead");

boar = state(7);
assert.equal(window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(boar, 8), "dead");

let giant = state(10);
assert.equal(window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(giant, 10), "zero_hp_prevention");
giant = state(10);
assert.equal(window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(giant, 11), "dead");

console.log("2014 browser Relentless regressions passed.");
