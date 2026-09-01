"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters-generated.js", "browser-condition-immunity.js", "browser-condition-rules.js",
  "browser-action-economy.js", "browser-modifiers.js", "browser-grapple.js", "browser-state.js", "browser-rolls.js",
  "browser-timed-conditions.js", "browser-source-bound-effects.js", "browser-undead-fortitude.js", "browser-zero-hp.js",
  "browser-attack.js", "browser-saves.js", "browser-healing.js", "browser-cleric-channel.js",
]) load(file);

const H = window.IRON_PIT_BROWSER_HEROES;
const M = window.IRON_PIT_BROWSER_MONSTERS;
const S = window.IRON_PIT_BROWSER_STATE;
const C = window.IRON_PIT_BROWSER_CLERIC_CHANNEL;
const T = window.IRON_PIT_BROWSER_TIMED;
const B = window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS;
const A = window.IRON_PIT_BROWSER_ATTACK;

const clericTemplate = H["seraphine-dawnshield-l2"];
assert.ok(clericTemplate, "Seraphine Cleric 2 must exist in the generated browser roster.");
assert.equal(clericTemplate.level, 2);
assert.equal(clericTemplate.max_hp, 17);
assert.deepEqual(clericTemplate.resources, {
  "adrenaline-rush": 2,
  "channel-divinity": 2,
  "relentless-endurance": 1,
  "spell-slot-1": 3,
});
assert.deepEqual(clericTemplate.canonical_prepared_spells.map((spell) => spell.id), [
  "bless", "cure-wounds", "guiding-bolt", "shield-of-faith", "healing-word",
]);
assert.deepEqual(clericTemplate.healingActions.map((spell) => spell.id), ["cure-wounds", "healing-word"]);
assert.equal(C.saveDc({ state: { template: clericTemplate } }), 13);
assert.equal(C.wisdomModifier({ state: { template: clericTemplate } }), 3);

const member = (template, id, side, position) => ({
  combatant_id: id, side, position_ft: position, state: S.buildState(structuredClone(template)),
});
const makeSetup = () => {
  const cleric = member(clericTemplate, "cleric", "heroes", 0);
  const skeleton = member(M["srd-skeleton"], "skeleton", "monsters", 10);
  const zombie = member(M["srd-ogre-zombie"], "zombie", "monsters", 15);
  return { cleric, skeleton, zombie, setup: { heroes: [cleric], monsters: [skeleton, zombie] } };
};
const fixedDice = (values) => {
  const queue = [...values];
  window.IRON_PIT_DICE = {
    roll: (sides) => {
      assert.ok(queue.length, `fixed dice exhausted before d${sides}`);
      const value = queue.shift();
      assert.ok(value >= 1 && value <= sides, `${value} is invalid for d${sides}`);
      return value;
    },
    rollMany: (count, sides) => Array.from({ length: count }, () => window.IRON_PIT_DICE.roll(sides)),
  };
};

{
  const { cleric, skeleton, zombie, setup } = makeSetup();
  const choice = C.choose(cleric, setup);
  assert.equal(choice.kind, "turn-undead");
  assert.deepEqual(choice.targets.map((target) => target.combatant_id), ["skeleton", "zombie"]);
  fixedDice([1, 1]);
  const resolved = C.resolve(1, 1, cleric, setup);
  assert.equal(resolved.sequence, 3);
  assert.equal(cleric.state.resources["channel-divinity"], 1);
  assert.equal(cleric.state.action_available, false);
  assert.deepEqual(resolved.events.map((event) => event.save_succeeded), [false, false]);
  for (const target of [skeleton, zombie]) {
    assert.ok(target.state.active_effect_ids.includes("turned-undead"));
    assert.ok(target.state.active_effect_ids.includes("frightened"));
    assert.ok(target.state.active_effect_ids.includes("incapacitated"));
    assert.equal(target.state.timed_effects.some((effect) => effect.turn_behavior === "forced_retreat"), true);
    assert.equal(target.state.timed_effects.every((effect) => effect.repeat_save_timing === null), true,
      "Turn Undead has one initial save only; it must not gain an invented repeat save.");
    assert.deepEqual([...new Set(target.state.timed_effects.map((effect) => effect.expires_round))], [11]);
  }
}

{
  const { cleric, skeleton, setup } = makeSetup();
  setup.monsters = [skeleton];
  fixedDice([1]); C.resolve(1, 1, cleric, setup);
  A.applyDamage(skeleton.state, 1, false, ["bludgeoning"], [cleric.state, skeleton.state]);
  assert.equal(skeleton.state.timed_effects.length, 0, "Any damage must end the whole Turn Undead effect group.");
  assert.equal(skeleton.state.active_effect_ids.includes("turned-undead"), false);
}

{
  const { cleric, skeleton, setup } = makeSetup();
  setup.monsters = [skeleton];
  fixedDice([1]); C.resolve(1, 1, cleric, setup);
  cleric.state.active_effect_ids.push("incapacitated");
  B.cleanupDisabledSources(setup);
  assert.equal(skeleton.state.timed_effects.length, 0, "Cleric incapacitation must end Turn Undead.");
}

{
  const { cleric, skeleton, setup } = makeSetup();
  setup.monsters = [skeleton];
  fixedDice([1]); C.resolve(1, 1, cleric, setup);
  let expiry = T.expireSourceStart(2, 10, cleric, setup);
  assert.equal(expiry.events.length, 0);
  assert.equal(skeleton.state.active_effect_ids.includes("turned-undead"), true);
  expiry = T.expireSourceStart(2, 11, cleric, setup);
  assert.deepEqual(expiry.events[0].removed_condition_ids, ["turned-undead", "frightened", "incapacitated"]);
  assert.equal(skeleton.state.timed_effects.length, 0);
}

{
  const { cleric, setup } = makeSetup();
  const goblin = member(M["srd-goblin-warrior"], "goblin", "monsters", 10);
  setup.monsters = [goblin];
  cleric.state.resources["spell-slot-1"] = 0;
  fixedDice([8, 20]);
  const result = C.resolve(1, 1, cleric, setup);
  assert.equal(result.events[0].feature_id, "divine-spark");
  assert.equal(result.events[0].save_succeeded, true);
  assert.equal(result.events[0].damage_roll.notation, "1d8+3");
  assert.equal(result.events[0].damage_roll.total, 5);
  assert.equal(cleric.state.resources["channel-divinity"], 1);
}

{
  const { cleric, skeleton, setup } = makeSetup();
  const ally = member(H["karnok-stoneward-l1"], "ally", "heroes", 5);
  ally.state.current_hp = 0; ally.state.is_unconscious = true;
  setup.heroes.push(ally); setup.monsters = [skeleton];
  cleric.state.resources["spell-slot-1"] = 0;
  fixedDice([8]);
  const result = C.resolve(1, 1, cleric, setup);
  assert.equal(result.events[0].feature_id, "divine-spark");
  assert.equal(result.events[0].healing_roll.total, 11);
  assert.equal(ally.state.current_hp, 11);
  assert.equal(ally.state.is_unconscious, false);
}

console.log("Browser Cleric 2 Channel Divinity, Turn Undead lifecycle, and Divine Spark regressions passed.");
