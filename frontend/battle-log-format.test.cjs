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
    event_type: "initiative", actor_name: "Veteran", description: "Veteran rolls initiative 19.",
    attack_roll: { selected_roll: 18, rolls: [7, 18], modifier: 1, total: 19, mode: "advantage" },
  });
  assert.match(text, /Veteran rolls initiative 19/);
  assert.match(text, /ADV \[7, 18\] 18 \+ 1 = 19/);
}

{
  const text = L.format({
    event_type: "death_save", actor_name: "Test Hero",
    death_save_roll: { selected_roll: 1 }, death_save_successes_before: 0, death_save_successes: 0,
    death_save_failures_before: 1, death_save_failures: 3, is_stable: false, is_dead: true,
  });
  assert.match(text, /NAT 1/); assert.match(text, /failures 1→3/); assert.match(text, /two failures/i); assert.match(text, /DEAD/);
}

{
  const lines = L.formatLines({
    event_type: "attack", actor_name: "Bandit", target_name: "Veteran", attack_name: "Scimitar",
    target_ac: 18, hit: true, critical: false,
    attack_roll: { selected_roll: 16, rolls: [16], modifier: 3, total: 19, mode: "normal" },
    damage_roll: { total: 6 }, damage_components: [{ total: 6, applied_total: 6, damage_type: "slashing" }],
    hp_before: 12, hp_after: 6, death_save_failures_before: 0, death_save_failures: 0,
    applied_condition_ids: [], is_dead: false,
  });
  assert.equal(lines[0], "Bandit uses Scimitar on Veteran.");
  assert.match(lines[1], /Attack: d20 16 \+ 3 = 19 vs AC 18 — HIT/);
  assert.equal(lines[2], "Damage: 6 slashing.");
  assert.equal(lines[3], "HP: Veteran 12 → 6.");
}

{
  const lines = L.formatLines({
    event_type: "attack", actor_name: "Purple Worm", target_name: "Pregen 2", attack_name: "Smack Down",
    target_ac: 18, hit: true, critical: false,
    attack_roll: { selected_roll: 12, rolls: [12], modifier: 9, total: 21, mode: "normal" },
    save_ability: "strength", save_dc: 18, save_succeeded: true,
    saving_throw_roll: { selected_roll: 16, rolls: [16], modifier: 5, total: 21, mode: "normal" },
    damage_roll: { total: 14 }, damage_components: [{ total: 14, applied_total: 14, damage_type: "bludgeoning" }],
    hp_before: 45, hp_after: 31, applied_condition_ids: [], is_dead: false,
  }, { attemptedConditionIds: ["prone"] });
  assert.equal(lines[0], "Purple Worm uses Smack Down on Pregen 2.");
  assert.match(lines[1], /d20 12 \+ 9 = 21 vs AC 18 — HIT/);
  assert.equal(lines[2], "Damage: 14 bludgeoning.");
  assert.match(lines.join("\n"), /Smack Down triggers Prone · STRENGTH DC 18/);
  assert.match(lines.join("\n"), /Save: Pregen 2 rolls d20 16 \+ 5 = 21 — SUCCESS/);
  assert.match(lines.join("\n"), /Condition: Pregen 2 resists Prone/);
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
  }, { attemptedConditionIds: ["prone"] });
  assert.match(text, /CONSTITUTION DC 13/); assert.match(text, /d20 5 \+ 2 = 7 — FAILURE/); assert.match(text, /gains Prone/);
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
  assert.match(text, /d20 19 \+ 5 \+ Bless 1d4 \[3\] = 27/);
  assert.match(text, /27 vs AC 13/);
  assert.match(text, /8 radiant \(16 before defenses → 8 after defenses\)/);
  assert.match(text, /Concentration ended: Shield Of Faith/);
}

{
  const text = L.format({
    event_type: "saving_throw", actor_name: "Acolyte", target_name: "Wolf",
    feature_id: "sacred-flame", save_ability: "dexterity", save_dc: 13, save_succeeded: false,
    saving_throw_roll: { selected_roll: 7, rolls: [7, 2], modifier: 2, total: 11, mode: "normal",
      bonus_dice: [{ source_effect_id: "bless", notation: "1d4", rolls: [2], total: 2 }] },
    damage_roll: { total: 7 }, damage_components: [{ total: 7, applied_total: 7, damage_type: "radiant" }],
    hp_before: 11, hp_after: 4, applied_condition_ids: [], is_dead: false,
  });
  assert.match(text, /Save: Wolf rolls/); assert.match(text, /11 vs DC 13 — FAILURE/);
  assert.match(text, /Bless 1d4 \[2\]/); assert.match(text, /7 radiant/); assert.match(text, /HP: Wolf 11 → 4/);
}

{
  const text = L.format({
    event_type: "saving_throw", actor_name: "Mage", target_name: "Paralyzed Target",
    feature_id: "test-effect", save_ability: "dexterity", save_dc: 15, save_succeeded: false,
    saving_throw_roll: null, applied_condition_ids: ["restrained"], hp_before: 8, hp_after: 8, is_dead: false,
  }, { attemptedConditionIds: ["restrained"] });
  assert.match(text, /AUTO FAIL vs DC 15 — FAILURE/); assert.match(text, /gains Restrained/);
}

{
  const text = L.format({
    event_type: "attack", actor_name: "Veteran", target_name: "Flesh Golem", attack_name: "Heavy Crossbow",
    target_ac: 9, hit: true, critical: false,
    attack_roll: { selected_roll: 11, rolls: [11], modifier: 3, total: 14, mode: "normal" },
    damage_roll: { total: 0 }, damage_components: [{ total: 10, applied_total: 0, damage_type: "piercing" }],
    hp_before: 93, hp_after: 93, applied_condition_ids: [], is_dead: false,
  });
  assert.match(text, /Damage: 0 piercing \(10 before defenses → 0 after defenses\)/);
  assert.doesNotMatch(text, /HP: Flesh Golem 93 →/);
}

{
  const events = [
    ...Array.from({ length: 6 }, (_, index) => ({
      sequence: index + 1, round_number: 1, event_type: "movement", actor_id: "golem-1", actor_name: "Flesh Golem",
      movement_ft: 5, movement_cost_ft: 5, description: "Flesh Golem moves 5 feet.",
    })),
    { sequence: 7, round_number: 1, event_type: "feature", actor_id: "golem-1", actor_name: "Flesh Golem", description: "Flesh Golem takes the Dodge action." },
  ];
  const compact = L.compactEvents(events);
  assert.equal(compact.length, 2);
  assert.equal(compact[0].movement_ft, 30);
  assert.equal(compact[0].movement_cost_ft, 30);
  assert.equal(compact[0].description, "Flesh Golem moves 30 feet.");
  assert.equal(compact[1].event_type, "feature");
}

console.log("Readable 2014 battle log regressions passed.");