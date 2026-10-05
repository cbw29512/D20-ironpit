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
    event_type: "initiative", actor_name: "Karnok Stoneward", description: "Karnok Stoneward rolls initiative 19.",
    attack_roll: { selected_roll: 18, rolls: [7, 18], modifier: 1, total: 19, mode: "advantage" },
  });
  assert.match(text, /Karnok Stoneward rolls initiative 19/);
  assert.match(text, /ADV \[7, 18\] 18 \+1 = 19/);
}

{
  const text = L.format({
    event_type: "death_save", actor_name: "Warlock 1 — Eldritch Blaster",
    death_save_roll: { selected_roll: 1 }, death_save_successes_before: 0, death_save_successes: 0,
    death_save_failures_before: 1, death_save_failures: 3, is_stable: false, is_dead: true,
  });
  assert.match(text, /NAT 1/); assert.match(text, /failures 1→3/); assert.match(text, /two failures/); assert.match(text, /DEAD/);
}

{
  const text = L.format({
    event_type: "attack", actor_name: "Roc", target_name: "Karnok Stoneward", attack_name: "Beak",
    target_ac: 17, hit: true, critical: false,
    attack_roll: { selected_roll: 12, rolls: [12], modifier: 13, total: 25, mode: "normal" },
    damage_roll: { total: 27 }, damage_components: [{ total: 27, applied_total: 27, damage_type: "piercing" }],
    hp_before: 12, hp_after: 0, death_save_failures_before: 0, death_save_failures: 0,
    applied_condition_ids: ["prone"], is_dead: false,
  });
  assert.match(text, /Roc → Karnok Stoneward/);
  assert.match(text, /Beak/);
  assert.match(text, /UNCONSCIOUS/);
  assert.doesNotMatch(text, /DEAD/);
}

{
  const text = L.format({
    event_type: "attack", actor_name: "Roc", target_name: "Seraphine Dawnshield", attack_name: "Talons",
    target_ac: 18, hit: true, critical: true,
    attack_roll: { selected_roll: 20, rolls: [20], modifier: 13, total: 33, mode: "normal" },
    damage_roll: { total: 8 }, damage_components: [{ total: 8, applied_total: 8, damage_type: "slashing" }],
    hp_before: 0, hp_after: 0, death_save_successes_before: 2, death_save_successes: 2,
    death_save_failures_before: 0, death_save_failures: 2, applied_condition_ids: [], is_dead: false,
  });
  assert.match(text, /Talons/);
  assert.match(text, /\+2 Death failures \(0→2\)/);
  assert.match(text, /UNCONSCIOUS/);
  assert.doesNotMatch(text, /now 0/);
  assert.doesNotMatch(text, /DEAD/);
}

{
  const text = L.format({
    event_type: "attack", actor_name: "Roc", target_name: "Seraphine Dawnshield", attack_name: "Talons",
    target_ac: 18, hit: true, critical: true,
    attack_roll: { selected_roll: 20, rolls: [20], modifier: 13, total: 33, mode: "normal" },
    damage_roll: { total: 40 }, damage_components: [{ total: 40, applied_total: 40, damage_type: "slashing" }],
    hp_before: 0, hp_after: 0, death_save_successes_before: 2, death_save_successes: 2,
    death_save_failures_before: 0, death_save_failures: 0, applied_condition_ids: [], is_dead: true,
  });
  assert.match(text, /instant death \(damage ≥ max HP\)/);
  assert.match(text, /DEAD/);
  assert.doesNotMatch(text, /\+2 Death failures \(now 0\)/);
}

{
  const text = L.format({
    event_type: "attack", actor_name: "Roc", target_name: "Karnok Stoneward", attack_name: "Beak",
    hit: true, critical: false, hp_before: 0, hp_after: 0, is_dead: true, is_stable: false,
  });
  assert.match(text, /DEAD/);
  assert.doesNotMatch(text, /UNCONSCIOUS/);
}

{
  const text = L.format({
    event_type: "attack", actor_name: "Fighter", target_name: "Ogre", attack_name: "Battleaxe",
    target_ac: 11, hit: true, critical: false,
    attack_roll: { selected_roll: 15, rolls: [15], modifier: 5, total: 20, mode: "normal" },
    save_ability: "constitution", save_dc: 13, save_succeeded: false,
    saving_throw_roll: { selected_roll: 5, rolls: [5], modifier: 2, total: 7, mode: "normal" },
    damage_roll: { total: 7 }, damage_components: [{ total: 7, applied_total: 7, damage_type: "slashing" }],
    hp_before: 30, hp_after: 23, applied_condition_ids: ["prone"], is_dead: false,
  });
  assert.match(text, /Ogre FAILS CONSTITUTION save/); assert.match(text, /d20 5 \+2 = 7 vs DC 13/); assert.match(text, /PRONE/);
}

{
  const text = L.format({
    event_type: "attack", actor_name: "Fighter", target_name: "Goblin", attack_name: "Greataxe",
    feature_id: "weapon-mastery-cleave", target_ac: 15, hit: true, critical: false,
    attack_roll: { selected_roll: 14, rolls: [14], modifier: 5, total: 19, mode: "normal" },
    damage_roll: { total: 6 }, damage_components: [{ total: 6, applied_total: 6, damage_type: "slashing" }],
    hp_before: 12, hp_after: 6, applied_condition_ids: [], is_dead: false,
  });
  assert.match(text, /Greataxe \[CLEAVE\]/); assert.match(text, /19 vs AC 15/); assert.match(text, /6 slashing/);
}

{
  const text = L.format({
    event_type: "attack", actor_name: "Cleric", target_name: "Ogre", attack_name: "Guiding Bolt",
    target_ac: 13, hit: true, critical: false,
    attack_roll: { selected_roll: 19, rolls: [19, 3], modifier: 5, total: 27, mode: "normal",
      bonus_dice: [{ source_effect_id: "bless", notation: "1d4", rolls: [3], total: 3 }] },
    damage_roll: { total: 8 }, damage_components: [{ total: 16, applied_total: 8, damage_type: "radiant" }],
    hp_before: 30, hp_after: 22, concentration_ended_effect_id: "shield-of-faith", is_dead: false,
  });
  assert.match(text, /d20 19 \+5 \+ Bless 1d4 \[3\] = 27/);
  assert.match(text, /27 vs AC 13/);
  assert.match(text, /8 radiant \(16 before defenses → 8 after defenses\)/);
  assert.match(text, /Concentration ended: Shield Of Faith/);
}

{
  const text = L.format({
    event_type: "saving_throw", actor_name: "Seraphine Dawnshield", target_name: "Wolf",
    feature_id: "sacred-flame", save_ability: "dexterity", save_dc: 13, save_succeeded: false,
    saving_throw_roll: { selected_roll: 7, rolls: [7, 2], modifier: 2, total: 11, mode: "normal",
      bonus_dice: [{ source_effect_id: "bless", notation: "1d4", rolls: [2], total: 2 }] },
    damage_roll: { total: 7 }, damage_components: [{ total: 7, applied_total: 7, damage_type: "radiant" }],
    hp_before: 11, hp_after: 4, applied_condition_ids: [], is_dead: false,
  });
  assert.match(text, /Wolf FAILS DEXTERITY save/); assert.match(text, /11 vs DC 13/);
  assert.match(text, /Bless 1d4 \[2\]/); assert.match(text, /7 radiant/); assert.match(text, /HP 11→4/);
}

{
  const text = L.format({
    event_type: "saving_throw", actor_name: "Mage", target_name: "Paralyzed Target",
    feature_id: "test-effect", save_ability: "dexterity", save_dc: 15, save_succeeded: false,
    saving_throw_roll: null, applied_condition_ids: ["restrained"], hp_before: 8, hp_after: 8, is_dead: false,
  });
  assert.match(text, /AUTO FAIL vs DC 15/); assert.match(text, /RESTRAINED/);
}

{
  const button = { disabled: true, listeners: {}, addEventListener(name, handler) { this.listeners[name] = handler; } };
  const status = { textContent: "" };
  global.document = {
    getElementById: (id) => ({ "download-log-button": button, status }[id] || null),
    createElement: () => ({ click() {}, remove() {} }),
    body: { append() {} },
  };
  global.URL = { createObjectURL: () => "blob:test", revokeObjectURL() {} };
  vm.runInThisContext(fs.readFileSync(path.join(__dirname, "battle-log-export.js"), "utf8"), { filename: "battle-log-export.js" });
  const exportLog = window.IRON_PIT_BATTLE_LOG_EXPORT;
  const battle = {
    events: [
      { round_number: 1, event_type: "initiative", actor_name: "Karnok Stoneward", description: "Karnok Stoneward rolls initiative 19." },
      {
        round_number: 1, event_type: "attack", actor_name: "Bandit", target_name: "Fighter", attack_name: "Scimitar",
        target_ac: 18, hit: true, critical: false,
        attack_roll: { selected_roll: 16, rolls: [16], modifier: 3, total: 19, mode: "normal" },
        damage_roll: { total: 6 }, damage_components: [{ total: 6, applied_total: 6, damage_type: "slashing" }],
        hp_before: 12, hp_after: 6, applied_condition_ids: [], is_dead: false,
        audit: { steps: [{ rule: "To hit", detail: "16 + 3 = 19 vs AC 18" }] },
      },
    ],
  };
  exportLog.install();
  assert.equal(button.disabled, true);
  exportLog.remember(battle);
  assert.equal(button.disabled, false);
  const text = exportLog.textFromBattle(battle);
  assert.match(text, /Round 1 · initiative/);
  assert.match(text, /Karnok Stoneward rolls initiative 19/);
  assert.match(text, /Bandit → Fighter/);
  assert.match(text, /6 slashing/);
  assert.match(text, /To hit: 16 \+ 3 = 19 vs AC 18/);
  assert.doesNotMatch(text, /placeholder|lorem|example fight/i);
  const spamBattle = {
    events: [{
      round_number: 1, event_type: "attack", actor_name: "Roc", target_name: "Karnok", attack_name: "Beak",
      hit: true, critical: false, hp_before: 12, hp_after: 0, is_dead: false,
      audit: { steps: [
        { phase: "action_selection", kind: "rule", label: "Roc: Beak" },
        { rule: "Resolution", detail: "Applied." },
        { step: "Resolution", outcome: "Applied." },
      ] },
    }],
  };
  const downloaded = exportLog.textFromBattle(spamBattle);
  assert.match(downloaded, /Roc: Beak/);
  assert.doesNotMatch(downloaded, /Resolution: Applied/);
  exportLog.remember({ events: [] });
  assert.equal(button.disabled, true);
}

console.log("Audit-grade battle log regressions passed.");

