"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-audit.js"), "utf8"), { filename: "browser-audit.js" });
const A = window.IRON_PIT_BROWSER_AUDIT;

const attack = {
  sequence: 7, round_number: 2, event_type: "attack", actor_id: "hero", actor_name: "Karnok",
  target_id: "monster", target_name: "Ogre", attack_name: "Greatsword", target_ac: 15, hit: true, critical: false,
  attack_roll: {
    notation: "1d20 [Heroic Inspiration]", rolls: [12], modifier: 5, selected_roll: 12, mode: "normal", total: 17,
    revisions: [{
      source_effect_id: "heroic-inspiration", kind: "die_replacement",
      original_rolls: [7], replacement_rolls: [12], original_modifier: 5, replacement_modifier: 5,
      original_selected: 7, replacement_selected: 12, original_total: 12, replacement_total: 17,
      accepted: "replacement", replaced_die_index: 0,
    }],
  },
  damage_roll: { notation: "2d6+3", rolls: [6, 5], modifier: 3, total: 14 },
  damage_components: [{
    source: "Greatsword", notation: "2d6+3", rolls: [6, 5], modifier: 3, damage_type: "slashing", total: 14, applied_total: 7,
    revisions: [{
      source_effect_id: "savage-attacker", kind: "roll_twice_choose",
      original_rolls: [2, 2], replacement_rolls: [6, 5], original_modifier: 3, replacement_modifier: 3,
      original_selected: null, replacement_selected: null, original_total: 7, replacement_total: 14,
      accepted: "replacement", replaced_die_index: null,
    }],
  }],
  temporary_hp_before: 5, temporary_hp_after: 0, hp_before: 20, hp_after: 18,
  applied_condition_ids: ["prone"], concentration_ended_effect_id: "bless", feature_id: "greatsword", resource_remaining: 0,
  is_dead: false, description: "Karnok hits Ogre.",
};

{
  const audited = A.annotateEvent(attack);
  assert.deepEqual(Object.fromEntries(Object.entries(audited).filter(([key]) => key !== "audit")), attack, "audit must not mutate mechanical fields");
  assert.equal(audited.audit.schema_version, 1);
  const phases = audited.audit.steps.map((item) => item.phase);
  assert.deepEqual(phases, [
    "action_selection", "roll", "reroll_or_replacement", "hit_or_save_check",
    "damage_roll", "reroll_or_replacement", "damage_applied",
    "state_change", "state_change", "state_change", "state_change", "resource_change",
  ]);
  assert.match(audited.audit.steps[2].label, /heroic inspiration.*original \[7\].*alternate \[12\].*accepted replacement/i);
  assert.match(audited.audit.steps[5].label, /savage attacker.*original \[2, 2\].*alternate \[6, 5\]/i);
  assert.match(audited.audit.steps[6].label, /14 before defenses → 7 applied/);
  assert.ok(audited.audit.steps.some((item) => item.label === "Temporary HP 5 → 0"));
  assert.ok(audited.audit.steps.some((item) => item.label === "HP 20 → 18"));
  assert.ok(audited.audit.steps.some((item) => item.label === "prone applied"));
  assert.ok(audited.audit.steps.some((item) => item.label === "Concentration ended: bless"));
}

{
  const initiative = A.annotateEvent({ round_number: 0, event_type: "initiative", actor_name: "Karnok", attack_roll: { notation: "1d20", rolls: [14], modifier: 2, selected_roll: 14, total: 16 } });
  assert.equal(initiative.audit.steps[0].phase, "initiative");
  assert.equal(initiative.audit.steps[1].phase, "roll");

  const precombat = A.annotateEvent({ round_number: 0, event_type: "feature", actor_name: "Cleric", feature_id: "shield-of-faith" });
  assert.equal(precombat.audit.steps[0].phase, "precombat");

  const victory = A.annotateEvent({ round_number: 3, event_type: "victory", actor_name: "Iron Pit", description: "Heroes win." });
  assert.equal(victory.audit.steps.at(-1).phase, "combat_end");
  assert.equal(victory.audit.steps.at(-1).kind, "outcome");
}

console.log("Browser rules-audit timing/evidence regressions passed.");
