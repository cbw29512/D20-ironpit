"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "battle-log-format.js"), "utf8"), { filename: "battle-log-format.js" });
const L = window.IRON_PIT_BATTLE_LOG;

{
  const text = L.format({
    event_type: "death_save", actor_name: "Warlock 1 — Eldritch Blaster",
    death_save_roll: { selected_roll: 1 }, death_save_successes_before: 0, death_save_successes: 0,
    death_save_failures_before: 1, death_save_failures: 3, is_stable: false, is_dead: true,
  });
  assert.match(text, /NAT 1/);
  assert.match(text, /failures 1→3/);
  assert.match(text, /two failures/);
  assert.match(text, /DEAD/);
}

{
  const text = L.format({
    event_type: "attack", actor_name: "Bandit", target_name: "Fighter", attack_name: "Scimitar",
    target_ac: 18, hit: true, critical: false, attack_roll: { selected_roll: 16, rolls: [16], modifier: 3, total: 19, mode: "normal" },
    damage_roll: { total: 6 }, damage_components: [{ applied_total: 6, damage_type: "slashing" }],
    hp_before: 12, hp_after: 6, death_save_failures_before: 0, death_save_failures: 0,
    applied_condition_ids: [], is_dead: false,
  });
  assert.match(text, /Bandit → Fighter/);
  assert.match(text, /19 vs AC 18/);
  assert.match(text, /6 slashing/);
  assert.match(text, /HP 12→6/);
}

console.log("Audit-grade battle log regressions passed.");
