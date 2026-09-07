"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
load("browser-turbo.js");

const selection = { hero_ids: ["hero"], monster_ids: ["monster"] };
const originalDice = { roll: () => 1, rollMany: (count) => Array(count).fill(1) };
window.IRON_PIT_DICE = originalDice;
window.IRON_PIT_BATTLE_LAB = {
  diagnosticId: (_heroes, _monsters, rolls) => `rolls-${rolls.map((item) => item.value).join("-")}`,
};

function member(id, hp) {
  return { combatant_id: id, state: { current_hp: hp, is_alive: hp > 0, is_dead: hp <= 0 } };
}

function deterministicEngine() {
  return {
    runEncounter: () => {
      const attack = window.IRON_PIT_DICE.roll(20), damage = window.IRON_PIT_DICE.roll(8);
      const heroesWin = attack >= 11;
      return {
        battle_id: `battle-${attack}-${damage}`,
        outcome: heroesWin ? "heroes_win" : "monsters_win",
        rounds: (damage % 4) + 1,
        setup: {
          heroes: [member("hero-1", heroesWin ? 5 : 0)],
          monsters: [member("monster-1", heroesWin ? 0 : 5)],
        },
        initiative: { turn_order: ["hero-1", "monster-1"] },
        events: [{ event_type: "attack", attack_roll: { selected_roll: attack }, damage_roll: { total: damage } }],
      };
    },
  };
}

(async () => {
  window.IRON_PIT_BROWSER_ENGINE = deterministicEngine();
  const first = window.IRON_PIT_BROWSER_TURBO.runSeeded(selection, 424242);
  const second = window.IRON_PIT_BROWSER_TURBO.runSeeded(selection, 424242);
  assert.deepEqual(first.battle, second.battle, "same seed must reproduce the same fight");
  assert.deepEqual(first.rolls, second.rolls, "same seed must reproduce every die result");
  assert.equal(window.IRON_PIT_DICE, originalDice, "seeded replay must restore secure production dice");

  const batchA = await window.IRON_PIT_BROWSER_TURBO.runBatch(selection, 100, 123456);
  const batchB = await window.IRON_PIT_BROWSER_TURBO.runBatch(selection, 100, 123456);
  assert.deepEqual(batchA, batchB, "same batch seed must reproduce the same 100-fight summary");
  assert.equal(batchA.requested_fights, 100);
  assert.equal(batchA.valid_fights + batchA.engine_errors, 100);
  assert.equal(batchA.heroes_wins + batchA.monsters_wins + batchA.draws, batchA.valid_fights);
  assert.equal(new Set(batchA.fights.map((fight) => fight.seed)).size, batchA.valid_fights);

  let calls = 0;
  const stable = deterministicEngine();
  window.IRON_PIT_BROWSER_ENGINE = {
    runEncounter: (current) => {
      calls += 1;
      if (calls === 2) throw new Error("synthetic engine rule error");
      return stable.runEncounter(current);
    },
  };
  const errorBatch = await window.IRON_PIT_BROWSER_TURBO.runBatch(selection, 3, 99);
  assert.equal(errorBatch.valid_fights, 2);
  assert.equal(errorBatch.engine_errors, 1);
  assert.equal(errorBatch.heroes_wins + errorBatch.monsters_wins + errorBatch.draws, 2, "engine errors must be excluded from win-rate denominator");
  assert.equal(errorBatch.errors[0].fight_number, 2);
  assert.equal(errorBatch.errors[0].message, "synthetic engine rule error");

  console.log("Browser Turbo/replay regressions passed.");
})().catch((error) => { console.error(error); process.exitCode = 1; });
