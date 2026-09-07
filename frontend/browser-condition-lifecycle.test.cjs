"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters-generated.js", "browser-condition-immunity.js", "browser-condition-rules.js",
  "browser-action-economy.js", "browser-grapple.js", "browser-modifiers.js", "browser-state.js", "browser-rage.js",
  "browser-rolls.js", "browser-timed-conditions.js", "browser-zero-hp.js", "browser-attack.js", "browser-saves.js",
  "browser-condition-lifecycle.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const T = window.IRON_PIT_BROWSER_TIMED;
const L = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE;
const A = window.IRON_PIT_BROWSER_ATTACK;
const V = window.IRON_PIT_BROWSER_SAVES;
const template = () => structuredClone(window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"]);
const member = (id, side = "heroes", source = template()) => ({ combatant_id: id, side, position_ft: 0, state: S.buildState(structuredClone(source)) });
let d20 = 1;
window.IRON_PIT_DICE = {
  roll: (sides) => sides === 20 ? d20 : 1,
  rollMany: (count, sides) => Array.from({ length: count }, () => sides === 20 ? d20 : 1),
};

{
  const target = member("poison-recovery-target");
  T.apply(target.state, "poisoned", "venom-source", {
    sourceEffectId: "venom-rider",
    appliedRound: 2,
    repeatSaveAbility: "constitution",
    repeatSaveDc: 15,
    repeatSaveTiming: "target_turn_end",
  });

  const sameRound = L.resolveTargetTiming(1, 2, target, "target_turn_start");
  assert.equal(sameRound.events.length, 0, "Poisoned must last through the round in which it is applied");
  assert.equal(target.state.active_effect_ids.includes("poisoned"), true);

  d20 = 1;
  const failed = L.resolveTargetTiming(sameRound.sequence, 3, target, "target_turn_start");
  assert.equal(failed.events.length, 1);
  assert.equal(failed.events[0].save_succeeded, false);
  assert.equal(target.state.active_effect_ids.includes("poisoned"), true);

  d20 = 20;
  const passed = L.resolveTargetTiming(failed.sequence, 4, target, "target_turn_start");
  assert.equal(passed.events.length, 1);
  assert.equal(passed.events[0].save_succeeded, true);
  assert.deepEqual(passed.events[0].removed_condition_ids, ["poisoned"]);
  assert.equal(target.state.active_effect_ids.includes("poisoned"), false);
}

{
  const source = member("source");
  const target = member("expiry-target");
  T.apply(target.state, "frightened", source.combatant_id, {
    sourceEffectId: "fear-effect",
    expiryTiming: "source_turn_start",
  });
  const setup = { heroes: [source, target], monsters: [] };
  const result = L.resolveSourceTiming(1, 4, source, setup, "source_turn_start");
  assert.equal(result.events.length, 1);
  assert.deepEqual(result.events[0].removed_condition_ids, ["frightened"]);
  assert.equal(target.state.active_effect_ids.includes("frightened"), false);
}

{
  const sourceA = member("source-a"), sourceB = member("source-b"), target = member("multi-source-target");
  T.apply(target.state, "frightened", sourceA.combatant_id, { sourceEffectId: "fear-a", expiryTiming: "source_turn_start" });
  T.apply(target.state, "frightened", sourceB.combatant_id, { sourceEffectId: "fear-b", expiryTiming: "source_turn_start" });
  const setup = { heroes: [sourceA, sourceB, target], monsters: [] };
  const first = L.resolveSourceTiming(1, 5, sourceA, setup, "source_turn_start");
  assert.equal(first.events.length, 0, "One source ending must not clear a condition still supplied by another source");
  assert.equal(target.state.active_effect_ids.includes("frightened"), true);
  const second = L.resolveSourceTiming(first.sequence, 5, sourceB, setup, "source_turn_start");
  assert.equal(second.events.length, 1);
  assert.equal(target.state.active_effect_ids.includes("frightened"), false);
}

{
  const source = member("monster-1:panache", "monsters"), target = member("hero-1:panache", "heroes");
  d20 = 1;
  const action = {
    id: "test-panache", name: "Enthralling Panache", saveAbility: "wisdom", dc: 20, range: 30,
    damageDiceCount: 0, damageDiceSize: 6, damageBonus: 0, damageType: null, successDamage: "none",
    failureConditions: [{ conditionId: "charmed", expiryTiming: "source_turn_start" }],
  };
  const event = V.resolveAction(1, 1, source, target, action, 5);
  assert.equal(event.save_succeeded, false); assert.deepEqual(event.applied_condition_ids, ["charmed"]);
  assert.equal(target.state.timed_effects[0].source_effect_id, "test-panache");
  assert.equal(target.state.timed_effects[0].expiry_timing, "source_turn_start");
  const ended = L.resolveSourceTiming(2, 2, source, { heroes: [target], monsters: [source] }, "source_turn_start");
  assert.deepEqual(ended.events[0].removed_condition_ids, ["charmed"]);
}

const ghoulTemplate = window.IRON_PIT_BROWSER_MONSTERS["srd-ghoul"];
assert.ok(ghoulTemplate, "Ghoul must be present in the generated browser runtime once certified");
const claw = ghoulTemplate.attacks.find((attack) => attack.name === "Claw");
assert.deepEqual(claw.controlEffect, {
  conditionId: "paralyzed", initialSaveAbility: "constitution", initialSaveDc: 10,
  excludedCreatureTypes: ["undead"], excludedSpeciesIds: ["elf"], expiryTiming: "target_turn_end",
});
const attackGhoul = (target, d20s) => {
  const source = member("monster-1:ghoul", "monsters", ghoulTemplate);
  const queue = [...d20s];
  window.IRON_PIT_DICE = {
    roll: (sides) => sides === 20 ? queue.shift() : 1,
    rollMany: (count, sides) => Array.from({ length: count }, () => sides === 20 ? queue.shift() : 1),
  };
  return A.resolveAttack(1, 1, source, target, claw, 5, { spendAction: false });
};

{
  const targetTemplate = template(); targetTemplate.creature_type = "Humanoid"; targetTemplate.species_id = "orc"; targetTemplate.armor_class = 10;
  const target = member("hero-ghoul-fail", "heroes", targetTemplate);
  const event = attackGhoul(target, [15, 5]);
  assert.equal(event.save_ability, "constitution"); assert.equal(event.save_dc, 10); assert.equal(event.save_succeeded, false);
  assert.ok(event.applied_condition_ids.includes("paralyzed"));
  assert.equal(target.state.timed_effects.find((effect) => effect.effect_id === "paralyzed").expiry_timing, "target_turn_end");
  assert.match(event.description, /Claw/); assert.match(event.description, /Paralyzed/);
}

{
  const targetTemplate = template(); targetTemplate.creature_type = "Humanoid"; targetTemplate.species_id = "orc"; targetTemplate.armor_class = 10;
  const target = member("hero-ghoul-pass", "heroes", targetTemplate);
  const event = attackGhoul(target, [15, 20]);
  assert.equal(event.save_succeeded, true); assert.equal(target.state.active_effect_ids.includes("paralyzed"), false);
}

for (const [creatureType, speciesId] of [["Undead", "human"], ["Humanoid", "elf"]]) {
  const targetTemplate = template(); targetTemplate.creature_type = creatureType; targetTemplate.species_id = speciesId; targetTemplate.armor_class = 10;
  const target = member(`hero-ghoul-excluded-${creatureType}-${speciesId}`, "heroes", targetTemplate);
  const event = attackGhoul(target, [15]);
  assert.equal(event.save_dc, null); assert.equal(event.saving_throw_roll, null); assert.equal(target.state.active_effect_ids.includes("paralyzed"), false);
}

console.log("Browser condition lifecycle and save-gated hit-condition regressions passed.");
