"use strict";

// Shared Charmed lifecycle: typed source capacity and source-side harm only.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = {
  immune: () => false,
};
load("browser-timed-conditions.js");
load("browser-source-target-capacity.js");
load("browser-failed-save-timed-effects.js");
load("browser-source-bound-effects.js");

const C = window.IRON_PIT_BROWSER_FAILED_SAVE_TIMED_EFFECTS;
const S = window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS;

function member(id, creatureType, side) {
  return {
    combatant_id: id, side, position_ft: 5,
    state: {
      template: { id, name: id, creature_type: creatureType, condition_immunities: [] },
      current_round: 1, turns_started: 0, current_hp: 30,
      is_dead: false, is_alive: true,
      active_effect_ids: [], timed_effects: [], active_curses: [], active_modifiers: [],
    },
  };
}

try {
  const owner = member("owner", "fey", "monsters");
  const friend = member("friend", "fey", "monsters");
  const human = [member("h1", "humanoid", "heroes"), member("h2", "humanoid", "heroes")];
  const beasts = Array.from({ length: 4 }, (_, index) => member(`beast-${index}`, "beast", "heroes"));
  const setup = { heroes: [...human, ...beasts], monsters: [owner, friend] };
  const action = { id: "renamed-charm", name: "Renamed Charm", magicalEffect: true };
  const rider = {
    effectId: "charmed", durationRounds: 14400, expiryTiming: "target_turn_end",
    sourceTargetLimitsByCreatureType: { humanoid: 1, beast: 3 },
    sourceEffectImmunityOnRepeatSaveSuccess: true, endsIfSourceDead: true,
    repeatSaveAbility: "wisdom",
    repeatSaveDc: 14, damageRepeatSaveTrigger: "source_or_allies",
  };
  const cast = (target) => C.apply(owner, target, action, rider, 1, setup);
  const owned = (target) => target.state.timed_effects.filter((effect) =>
    effect.effect_id === "charmed" && effect.source_id === owner.combatant_id
      && effect.source_effect_id === action.id);

  [human[0], beasts[0], beasts[1], beasts[2], human[1]].forEach(cast);
  assert.equal(owned(human[0]).length, 0, "New humanoid displaces old humanoid");
  assert.equal(owned(human[1]).length, 1);
  beasts.slice(0, 3).forEach((beast) => assert.equal(owned(beast).length, 1));
  cast(beasts[3]);
  assert.equal(owned(beasts[0]).length, 0, "Fourth beast displaces only a beast");
  assert.equal(owned(human[1]).length, 1, "Beast capacity must not evict humanoid");
  beasts.slice(1).forEach((beast) => assert.equal(owned(beast).length, 1));
  assert.equal(C.isImmune(human[0], action, owner.combatant_id), false);
  assert.equal(C.isImmune(beasts[0], action, owner.combatant_id), false);

  const victim = beasts[1];
  let saveCount = 0;
  window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE = {
    repeatSave: () => {
      saveCount += 1;
      return { succeeded: false, buffs: [], roll: null };
    },
  };
  assert.equal(S.resolveDamageRepeatSaves(1, 1, human[1], victim, setup).events.length, 0);
  assert.equal(saveCount, 0, "Enemy-side harm must not trigger source-side save");
  assert.equal(S.resolveDamageRepeatSaves(1, 1, friend, victim, setup).events.length, 1);
  assert.equal(saveCount, 1, "Owner ally damage must trigger repeat save");
  assert.equal(S.resolveDamageRepeatSaves(2, 1, owner, victim, setup).events.length, 1);
  assert.equal(saveCount, 2, "Owner damage must trigger repeat save");
  window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.repeatSave = () => ({
    succeeded: true, buffs: [], roll: null,
  });
  const saved = S.resolveDamageRepeatSaves(3, 1, owner, victim, setup);
  assert.equal(saved.events.length, 1);
  assert.equal(saved.events[0].save_succeeded, true);
  assert.equal(C.isImmune(victim, action, owner.combatant_id), true,
    "A successful repeat save must grant the printed source immunity");
  assert.equal(owned(victim).length, 0);

  owner.state.is_dead = true;
  S.cleanupDisabledSources(setup);
  assert.equal(owned(beasts[2]).length, 0);
  assert.equal(C.isImmune(beasts[2], action, owner.combatant_id), false,
    "Owner death releases control without a successful-save immunity");

  assert.throws(() => window.IRON_PIT_BROWSER_SOURCE_TARGET_CAPACITY.enforce(
    owner, victim, action.id, "charmed", 20, setup, { humanoid: 1 },
  ), /Creature type lacks printed source capacity/);
} catch (error) {
  console.error("Browser shared Fey Charm regressions failed.", error);
  throw error;
}
console.log("Browser shared Fey Charm capacity/harm regressions passed.");
