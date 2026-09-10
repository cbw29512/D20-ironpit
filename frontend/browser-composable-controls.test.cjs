"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

for (const file of [
  "browser-heroes.js",
  "browser-monsters-generated.js",
  "browser-condition-immunity.js",
  "browser-condition-rules.js",
  "browser-action-economy.js",
  "browser-grapple.js",
  "browser-timed-conditions.js",
  "browser-modifiers.js",
  "browser-state.js",
  "browser-rage.js",
  "browser-rolls.js",
  "browser-zero-hp.js",
  "browser-attack.js",
  "browser-resources.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const A = window.IRON_PIT_BROWSER_ATTACK;
const heroes = window.IRON_PIT_BROWSER_HEROES;
const monsters = window.IRON_PIT_BROWSER_MONSTERS;

const member = (id, side, template, position) => ({
  combatant_id: id,
  side,
  position_ft: position,
  state: S.buildState(structuredClone(template)),
});

const queuedDice = (values, fallback = 10) => {
  const queue = [...values];
  const roll = (sides) => ((queue.length ? queue.shift() : fallback) - 1) % sides + 1;
  return {
    roll,
    rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)),
  };
};

const attacker = member("monster:test", "monsters", monsters["srd-commoner"], 5);
const target = member("hero:test", "heroes", heroes["karnok-stoneward-l1"], 0);
const baseAttack = attacker.state.template.attacks[0];
const attack = {
  ...baseAttack,
  id: "test-composable-control",
  controlEffect: {
    maxTargetSize: "large",
    grappleEscapeDc: 15,
    restrainsWhileGrappled: true,
    conditionId: "blinded",
    repeatSaveAbility: "constitution",
    repeatSaveDc: 15,
    repeatSaveTiming: "target_turn_end",
  },
};

window.IRON_PIT_DICE = queuedDice([20, 4]);
const event = A.resolveAttack(1, 1, attacker, target, attack, 5);

assert.equal(event.hit, true);
assert.deepEqual(event.applied_condition_ids, ["grappled", "restrained", "blinded"]);
assert.equal(target.state.grapple_sources[0].escape_dc, 15);
assert.equal(target.state.active_effect_ids.includes("restrained"), true);
assert.equal(target.state.active_effect_ids.includes("blinded"), true);
assert.equal(target.state.timed_effects[0].repeat_save_ability, "constitution");
assert.equal(target.state.timed_effects[0].repeat_save_dc, 15);
assert.equal(target.state.timed_effects[0].repeat_save_timing, "target_turn_end");

console.log("Composable grapple plus timed-condition browser regression passed.");
