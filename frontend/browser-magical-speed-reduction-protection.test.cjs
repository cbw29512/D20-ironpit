"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
load("browser-modifiers.js");

const M = window.IRON_PIT_BROWSER_MODIFIERS;

function state(protectedByMagicDefense) {
  return {
    template: { speed_ft: 30 },
    exhaustion_level: 0,
    active_modifiers: [
      {
        id: "magic-slow", source_id: "caster", source_effect_id: "slow-effect",
        kind: "speed", flat_bonus: -10, source_is_magical: true,
      },
      {
        id: "mud-slow", source_id: "hazard", source_effect_id: "mud-effect",
        kind: "speed", flat_bonus: -5, source_is_magical: false,
      },
    ],
    timed_effects: protectedByMagicDefense
      ? [{ effect_id: "movement-protection", source_id: "ally", prevents_magical_speed_reduction: true }]
      : [],
  };
}

assert.equal(M.effectiveSpeed(state(true)), 25,
  "magical speed penalty should be ignored while generic protection is active");
assert.equal(M.effectiveSpeed(state(false)), 15,
  "magical speed penalty should return when protection is absent");

console.log("Browser magical speed-reduction protection parity regressions passed.");
