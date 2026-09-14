"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-grid-geometry.js", "browser-area-shapes.js", "browser-area-targeting.js",
  "browser-modifiers.js", "browser-condition-rules.js", "browser-concentration.js",
  "browser-spell-effects.js", "browser-spell-modifiers.js",
]) load(file);

const U = window.IRON_PIT_BROWSER_AREA_TARGETING;
const M = window.IRON_PIT_BROWSER_MODIFIERS;
const Q = window.IRON_PIT_BROWSER_CONDITION_RULES;
const C = window.IRON_PIT_BROWSER_CONCENTRATION;
const SM = window.IRON_PIT_BROWSER_SPELL_MODIFIERS;
const shared = window.IRON_PIT_BROWSER_SPELL_EFFECTS["faerie-fire"];
const spell = { id: "faerie-fire", name: "Faerie Fire", concentration: true };

function state(active = []) {
  return {
    active_effect_ids: [...active], active_modifiers: [], timed_effects: [], concentration: null,
    is_dead: false, is_unconscious: false,
  };
}

assert.equal(shared.durationMinutes, 1);
assert.deepEqual(shared.failureModifierEffects.map((effect) => effect.kind), [
  "attacks-against-advantage", "invisibility-suppressed",
]);

{
  const owner = state(), target = state(["invisible"]), states = [owner, target];
  SM.startSave(owner, "caster", spell, 1, states);
  SM.applyFailedSave("target", target, "caster", spell, 1);
  assert.equal(M.attacksAgainstAdvantage(target), 1);
  assert.equal(M.invisibilitySuppressed(target), true);
  assert.equal(Q.has(target, "invisible"), false);
  assert.equal(C.end(owner, states), true);
  assert.equal(M.attacksAgainstAdvantage(target), 0);
  assert.equal(M.invisibilitySuppressed(target), false);
  assert.equal(Q.has(target, "invisible"), true);
}

function member(id, side, x, y) {
  return {
    combatant_id: id, side,
    state: {
      position: { x, y }, template: { size: "medium" },
      is_alive: true, is_dead: false, current_hp: 10,
    },
  };
}

{
  const caster = member("caster", "heroes", 1, 1);
  const first = member("first", "monsters", 5, 3);
  const second = member("second", "monsters", 6, 3);
  const setup = {
    heroes: [caster], monsters: [first, second],
    map_definition: { width_squares: 12, height_squares: 8, cell_size_ft: 5 },
  };
  const area = { shape: "cube", origin: "point", length_ft: 20 };
  const placements = U.legalPlacements(caster, setup, area, 60);
  assert.ok(placements.some((placement) => new Set(placement.enemyIds).size === 2));
}

console.log("Shared Faerie Fire browser regressions passed.");
