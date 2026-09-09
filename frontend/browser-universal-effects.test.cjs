"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters.js", "browser-condition-immunity.js", "browser-condition-rules.js",
  "browser-action-economy.js", "browser-grapple.js", "browser-timed-conditions.js", "browser-persistent-effects.js",
  "browser-modifiers.js", "browser-state.js", "browser-rolls.js", "browser-zero-hp.js", "browser-attack.js", "browser-saves.js",
]) load(file);

const queuedDice = (values, fallback = 10) => {
  const queue = [...values];
  const roll = (sides) => ((queue.length ? queue.shift() : fallback) - 1) % sides + 1;
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
};
const S = window.IRON_PIT_BROWSER_STATE;
const A = window.IRON_PIT_BROWSER_ATTACK;
const V = window.IRON_PIT_BROWSER_SAVES;
const M = window.IRON_PIT_BROWSER_MODIFIERS;
const heroes = window.IRON_PIT_BROWSER_HEROES;
const monsters = window.IRON_PIT_BROWSER_MONSTERS;
const member = (id, side, template, position = side === "heroes" ? 0 : 5) => ({
  combatant_id: id, side, position_ft: position, state: S.buildState(structuredClone(template)),
});

{
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
  const commoner = member("monster-1:commoner", "monsters", monsters["srd-commoner"]);
  const attack = {
    ...commoner.state.template.attacks[0],
    bonus: 100,
    persistentEffects: [
      { grappleEscapeDc: 14, restrainsWhileGrappled: true },
      { conditionId: "blinded" },
    ],
  };
  window.IRON_PIT_DICE = queuedDice([10, 1]);
  const event = A.resolveAttack(1, 1, commoner, hero, attack, 5);
  assert.equal(event.hit, true);
  assert.ok(event.applied_condition_ids.includes("grappled"));
  assert.ok(event.applied_condition_ids.includes("restrained"));
  assert.ok(event.applied_condition_ids.includes("blinded"));
  assert.equal(hero.state.grapple_sources[0].escape_dc, 14);
}

{
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"]);
  const commoner = member("monster-1:commoner", "monsters", monsters["srd-commoner"]);
  const baseSpeed = hero.state.template.speed_ft;
  const action = {
    id: "control-burst", name: "Control Burst", saveAbility: "strength", dc: 30, range: 5,
    damageDiceCount: 0, damageDiceSize: 6, damageBonus: 0, damageType: null, successDamage: "none",
    persistentEffects: [
      { grappleEscapeDc: 14, restrainsWhileGrappled: true },
      { conditionId: "blinded" },
    ],
    onFailureModifiers: [{ kind: "speed", flatBonus: -10, expiresAtEndOfTargetTurn: true }],
  };
  window.IRON_PIT_DICE = queuedDice([20]);
  const event = V.resolveAction(1, 1, commoner, hero, action, 5);
  assert.equal(event.save_succeeded, false);
  assert.ok(event.applied_condition_ids.includes("grappled"));
  assert.ok(event.applied_condition_ids.includes("restrained"));
  assert.ok(event.applied_condition_ids.includes("blinded"));
  assert.equal(M.effectiveSpeed(hero.state), baseSpeed - 10);
}

console.log("Browser universal persistent-effect pipeline regressions passed.");
