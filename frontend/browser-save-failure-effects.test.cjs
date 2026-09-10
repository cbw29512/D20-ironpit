"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters.js", "browser-condition-immunity.js", "browser-condition-rules.js",
  "browser-action-economy.js", "browser-grapple.js", "browser-timed-conditions.js", "browser-modifiers.js",
  "browser-state.js", "browser-rage.js", "browser-rolls.js", "browser-zero-hp.js", "browser-attack.js",
  "browser-save-failure-effects.js", "browser-saves.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const M = window.IRON_PIT_BROWSER_MODIFIERS;
const V = window.IRON_PIT_BROWSER_SAVES;
const heroes = window.IRON_PIT_BROWSER_HEROES;
const monsters = window.IRON_PIT_BROWSER_MONSTERS;
const member = (id, side, template, position) => ({
  combatant_id: id, side, position_ft: position, state: S.buildState(structuredClone(template)),
});
const dice = (value) => {
  window.IRON_PIT_DICE = {
    roll: (sides) => sides === 20 ? value : 1,
    rollMany: (count, sides) => Array.from({ length: count }, () => sides === 20 ? value : 1),
  };
};
const action = (dc = 30) => ({
  id: "test-failed-save-riders", name: "Test Failed Save Riders", saveAbility: "dexterity", dc, range: 30,
  damageDiceCount: 0, damageDiceSize: 6, damageBonus: 0, damageType: null, successDamage: "none",
  failureEffects: [
    { kind: "prone" },
    { kind: "condition", condition: "frightened", expiryTiming: "target_turn_end" },
    { kind: "speed", flatBonus: -10, expiresAtEndOfTargetTurn: true },
  ],
  animation: "save-effect",
});

{
  const actor = member("monster-1:commoner", "monsters", monsters["srd-commoner"], 5);
  const target = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"], 0);
  dice(1);
  const event = V.resolveAction(1, 1, actor, target, action(), 5, { spendAction: false, setup: { heroes: [target], monsters: [actor] } });
  assert.equal(event.save_succeeded, false);
  assert.deepEqual(event.applied_condition_ids, ["prone", "frightened"]);
  assert.deepEqual(target.state.active_effect_ids.slice(-2), ["prone", "frightened"]);
  assert.equal(target.state.timed_effects[0].source_effect_id, action().id);
  assert.equal(M.effectiveSpeed(target.state), target.state.template.speed_ft - 10);
  assert.match(target.state.active_modifiers[0].id, /failed-save-modifier:2$/);
}

{
  const actor = member("monster-1:commoner", "monsters", monsters["srd-commoner"], 5);
  const target = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"], 0);
  dice(20);
  const event = V.resolveAction(1, 1, actor, target, action(1), 5, { spendAction: false });
  assert.equal(event.save_succeeded, true);
  assert.deepEqual(event.applied_condition_ids, []);
  assert.equal(target.state.active_effect_ids.includes("prone"), false);
  assert.equal(target.state.active_effect_ids.includes("frightened"), false);
  assert.deepEqual(target.state.active_modifiers, []);
}

{
  const actor = member("monster-1:commoner", "monsters", monsters["srd-commoner"], 5);
  const target = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"], 0);
  const gated = action();
  gated.failureEffects = [{ kind: "prone", maxTargetSize: "small" }, { kind: "speed", flatBonus: -5 }];
  dice(1);
  const event = V.resolveAction(1, 1, actor, target, gated, 5, { spendAction: false });
  assert.deepEqual(event.applied_condition_ids, []);
  assert.equal(target.state.active_effect_ids.includes("prone"), false);
  assert.equal(M.effectiveSpeed(target.state), target.state.template.speed_ft - 5);
}

console.log("Browser universal failed-save effect regressions passed.");
