"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
load("browser-regeneration.js");

function state(profile, hp = 5) {
  return {
    template: { name: "Regenerator", regeneration: profile }, current_hp: hp, max_hp_bonus: 0,
    is_alive: true, is_dead: false, is_unconscious: false, is_stable: false,
    death_save_successes: 0, death_save_failures: 0, regeneration_suppressed: false,
  };
}
window.IRON_PIT_BROWSER_STATE = { effectiveMaxHp: () => 30 };

{
  const target = state({ amount: 10, requiresPositiveHp: true, suppressedByDamageTypes: [], survivesZeroUntilTurn: false }, 12);
  const member = { combatant_id: "monster-1", state: target };
  const result = window.IRON_PIT_BROWSER_REGENERATION.startTurn(1, 2, member);
  assert.equal(target.current_hp, 22);
  assert.equal(result.event.hp_before, 12);
  assert.equal(result.died, false);
}

{
  const target = state({ amount: 10, requiresPositiveHp: false, suppressedByDamageTypes: ["fire"], survivesZeroUntilTurn: true }, 0);
  const member = { combatant_id: "troll", state: target };
  window.IRON_PIT_BROWSER_REGENERATION.noteSuppression(target, ["fire"]);
  const result = window.IRON_PIT_BROWSER_REGENERATION.startTurn(1, 2, member);
  assert.equal(result.died, true);
  assert.equal(target.is_dead, true);
  assert.equal(target.current_hp, 0);
}

{
  const target = state({ amount: 10, requiresPositiveHp: false, suppressedByDamageTypes: ["fire"], survivesZeroUntilTurn: true }, 0);
  const member = { combatant_id: "troll", state: target };
  const result = window.IRON_PIT_BROWSER_REGENERATION.startTurn(1, 2, member);
  assert.equal(result.died, false);
  assert.equal(target.current_hp, 10);
  assert.equal(target.is_unconscious, false);
}

console.log("2014 browser Regeneration regressions passed.");
