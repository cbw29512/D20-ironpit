"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "battle-lab.js"), "utf8"), { filename: "battle-lab.js" });

const lab = window.IRON_PIT_BATTLE_LAB;

{
  const first = lab.createSeededDice("smoke-1");
  const second = lab.createSeededDice("smoke-1");
  const different = lab.createSeededDice("smoke-2");
  const a = Array.from({ length: 20 }, () => first.roll(20));
  const b = Array.from({ length: 20 }, () => second.roll(20));
  const c = Array.from({ length: 20 }, () => different.roll(20));
  assert.deepEqual(a, b, "the same seed must reproduce the same dice sequence");
  assert.notDeepEqual(a, c, "different seeds should not collapse to the same test sequence");
  assert.ok(a.every((value) => value >= 1 && value <= 20));
}

{
  const dice = lab.createSeededDice("pool");
  assert.equal(dice.rollMany(4, 6).length, 4);
  assert.throws(() => dice.roll(1), /Die sides/);
  assert.throws(() => dice.rollMany(0, 6), /Dice count/);
}

{
  const battle = {
    battle_id: "ignored",
    outcome: "heroes_win",
    rounds: 2,
    initiative: { turn_order: ["hero-1:test", "monster-1:test"] },
    setup: {
      heroes: [{ combatant_id: "hero-1:test", state: { current_hp: 5, temporary_hp: 0, is_alive: true, is_dead: false, is_stable: false, death_save_successes: 0, death_save_failures: 0 } }],
      monsters: [{ combatant_id: "monster-1:test", state: { current_hp: 0, temporary_hp: 0, is_alive: false, is_dead: true, is_stable: false, death_save_successes: 0, death_save_failures: 0 } }],
    },
    events: [
      { round_number: 1, event_type: "attack", actor_id: "hero-1:test", target_id: "monster-1:test", hit: true, critical: true, attack_roll: { mode: "normal", selected_roll: 20, total: 25 }, damage_roll: { total: 8 }, hp_before: 8, hp_after: 0, weapon_id: "test-sword" },
      { round_number: 2, event_type: "victory", actor_id: "arena" },
    ],
  };
  const same = structuredClone(battle); same.battle_id = "different-id";
  assert.equal(lab.fingerprint(battle), lab.fingerprint(same), "non-mechanical battle IDs must not affect replay comparison");
  assert.match(lab.summary(battle, "smoke-1", "exact replay reproduced"), /Seed smoke-1 · 2 rounds · 1 attacks · 1 criticals · 0 heals · exact replay reproduced/);
}

console.log("battle lab deterministic utilities passed");
