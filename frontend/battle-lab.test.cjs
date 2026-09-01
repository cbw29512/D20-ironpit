"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "battle-lab.js"), "utf8"), { filename: "battle-lab.js" });

const lab = window.IRON_PIT_BATTLE_LAB;

{
  const rolls = [{ sides: 20, value: 17 }, { sides: 6, value: 4 }, { sides: 8, value: 7 }];
  const first = lab.diagnosticId(["hero-a"], ["monster-a"], rolls);
  const second = lab.diagnosticId(["hero-a"], ["monster-a"], structuredClone(rolls));
  assert.equal(first, second, "the same real roll tape must produce the same diagnostic ID");
  assert.notEqual(first, lab.diagnosticId(["hero-a"], ["monster-a"], [...rolls, { sides: 4, value: 2 }]));
  assert.match(first, /^[0-9a-f]{8}$/);
}

{
  const battle = {
    battle_id: "ignored", outcome: "heroes_win", rounds: 2,
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
  assert.equal(lab.fingerprint(battle), lab.fingerprint(same), "non-mechanical battle IDs must not affect fingerprints");
  assert.match(lab.summary(battle, [{ sides: 20, value: 20 }], "abc12345"), /Battle abc12345 · 1 secure dice rolls · 2 rounds · 1 attacks · 1 criticals · 0 heals/);
}

assert.equal("createSeededDice" in lab, false, "Battle Lab must never expose an alternate seeded combat RNG");
console.log("battle lab production-path diagnostics passed");
