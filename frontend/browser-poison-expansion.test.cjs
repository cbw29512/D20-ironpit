"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters-generated.js", "browser-condition-immunity.js", "browser-condition-rules.js",
  "browser-action-economy.js", "browser-grapple.js", "browser-timed-conditions.js", "browser-modifiers.js",
  "browser-state.js", "browser-rage.js", "browser-sneak-attack.js", "browser-rolls.js", "browser-undead-fortitude.js",
  "browser-zero-hp.js", "browser-attack.js", "browser-saves.js", "browser-condition-lifecycle.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const A = window.IRON_PIT_BROWSER_ATTACK;
const L = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE;
const monsters = window.IRON_PIT_BROWSER_MONSTERS;
const heroes = window.IRON_PIT_BROWSER_HEROES;
const member = (id, side, template, position) => ({
  combatant_id: id, side, position_ft: position, state: S.buildState(structuredClone(template)),
});
const setD20 = (value) => {
  window.IRON_PIT_DICE = {
    roll: (sides) => sides === 20 ? value : 1,
    rollMany: (count, sides) => Array.from({ length: count }, () => sides === 20 ? value : 1),
  };
};
const assertArenaPoison = (target) => {
  const poison = target.state.timed_effects.find((effect) => effect.effect_id === "poisoned");
  assert.ok(poison);
  assert.equal(poison.expiry_timing, null);
  assert.equal(poison.expires_at_start_of_source_turn, false);
  assert.equal(poison.repeat_save_ability, "constitution");
  assert.equal(poison.repeat_save_dc, 10);
  assert.equal(poison.repeat_save_timing, "target_turn_start");
};

{
  const vultureTemplate = monsters["srd-giant-vulture"];
  assert.ok(vultureTemplate);
  assert.equal(vultureTemplate.speed_ft, 60);
  assert.ok(vultureTemplate.traits.includes("pack-tactics"));
  assert.ok(vultureTemplate.damage_resistances.includes("necrotic"));
  const gouge = vultureTemplate.attacks.find((attack) => attack.id === "giant-vulture-gouge");
  assert.deepEqual(gouge.controlEffect, { conditionId: "poisoned", expiryTiming: "target_turn_end" });

  const source = member("monster-1:vulture", "monsters", vultureTemplate, 5);
  const target = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"], 0);
  setD20(15);
  const event = A.resolveAttack(1, 1, source, target, gouge, 5, { spendAction: false, setup: { heroes: [target], monsters: [source] } });
  assert.equal(event.hit, true);
  assert.ok(event.applied_condition_ids.includes("poisoned"));
  assertArenaPoison(target);
  setD20(20);
  const sameRound = L.resolveTargetTiming(2, 1, target, "target_turn_start");
  assert.equal(sameRound.events.length, 0, "arena Poisoned must last through the round in which it was applied");
  const ended = L.resolveTargetTiming(sameRound.sequence, 2, target, "target_turn_start");
  assert.equal(ended.events.length, 1);
  assert.deepEqual(ended.events[0].removed_condition_ids, ["poisoned"]);
}

{
  const wyvernTemplate = monsters["srd-wyvern"];
  assert.ok(wyvernTemplate);
  assert.equal(wyvernTemplate.speed_ft, 80);
  assert.deepEqual(wyvernTemplate.attack_action.slots.map((slot) => slot.attackIds), [["wyvern-bite"], ["wyvern-sting"]]);
  const sting = wyvernTemplate.attacks.find((attack) => attack.id === "wyvern-sting");
  assert.deepEqual(sting.onHitDamage, [{ source: "Poison", diceCount: 7, diceSize: 6, damageBonus: 0, damageType: "poison" }]);
  assert.deepEqual(sting.controlEffect, {
    conditionId: "poisoned",
    expiresAtStartOfSourceTurn: true,
    expiryTiming: "source_turn_start",
  });

  const source = member("monster-1:wyvern", "monsters", wyvernTemplate, 10);
  const target = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"], 0);
  const setup = { heroes: [target], monsters: [source] };
  setD20(15);
  const event = A.resolveAttack(1, 1, source, target, sting, 10, { spendAction: false, setup });
  assert.equal(event.hit, true);
  assert.ok(event.applied_condition_ids.includes("poisoned"));
  assertArenaPoison(target);
  setD20(20);
  const ended = L.resolveTargetTiming(2, 2, target, "target_turn_start");
  assert.equal(ended.events.length, 1);
  assert.deepEqual(ended.events[0].removed_condition_ids, ["poisoned"]);
}

console.log("Generated Giant Vulture/Wyvern source fidelity and next-round arena Poisoned policy regressions passed.");
