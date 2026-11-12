"use strict";

// Iron Pit policy: Draining Kiss has no willing-target branch; only source-owned Charm.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
window.IRON_PIT_BROWSER_STATE = { sizeAtMost: () => true, distance: () => 5 };
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = {
  immune: (state, id, _source, options = {}) => Boolean(
    id === "charmed" && options.sourceIsMagical && state.magical_charm_suppressed,
  ),
};
load("browser-condition-rules.js");
load("browser-save-action-support.js");

function member(id, side, sourceId = null) {
  return {
    combatant_id: id,
    side,
    state: {
      template: { creature_type: "humanoid", name: id },
      active_effect_ids: sourceId ? ["charmed"] : [],
      timed_effects: sourceId ? [{
        effect_id: "charmed", source_id: sourceId, source_is_magical: false,
      }] : [],
      willing_attack_source_ids: [],
      grapple_sources: [],
      current_hp: 80,
      is_alive: true,
      is_dead: false,
    },
  };
}

const actor = member("succubus", "monsters");
const action = {
  id: "draining-kiss",
  name: "Draining Kiss",
  range: 5,
  requiresTargetSight: false,
  targetScope: "enemies",
  targetQualification: { anyOf: ["source_charmed"] },
};
const legal = (target, selectedAction = action, distance = 5) =>
  window.IRON_PIT_BROWSER_SAVE_ACTION_SUPPORT.legalAction(
    selectedAction, target, distance, actor.combatant_id, actor,
  );

try {
  assert.equal(legal(member("unqualified-enemy", "heroes")), false);
  assert.equal(legal(member("other-charmer", "heroes", "another-source")), false);
  assert.equal(legal(member("owned-charm", "heroes", actor.combatant_id)), true);

  const ally = member("ally", "monsters");
  assert.equal(legal(ally), false);
  ally.state.willing_attack_source_ids.push(actor.combatant_id);
  assert.equal(legal(ally), false, "Willing allies cannot volunteer for hostile Draining Kiss.");
  assert.equal(legal(actor), false, "The acting source is never a target.");

  const willingEnemy = member("willing-enemy", "heroes");
  willingEnemy.state.willing_attack_source_ids.push(actor.combatant_id);
  assert.equal(legal(willingEnemy), false, "Willingness is not a valid arena gate.");
  assert.equal(legal(willingEnemy, action, 10), false, "Normal range still applies.");

  // Even if an ally becomes source-Charmed, this hostile action targets enemies.
  ally.state.active_effect_ids.push("charmed");
  ally.state.timed_effects.push({
    effect_id: "charmed", source_id: actor.combatant_id, source_is_magical: false,
  });
  assert.equal(legal(ally), false);

  const suppressed = member("suppressed-owner", "heroes");
  suppressed.state.active_effect_ids.push("charmed");
  suppressed.state.timed_effects = [
    { effect_id: "charmed", source_id: actor.combatant_id, source_is_magical: true },
    { effect_id: "charmed", source_id: "other-source", source_is_magical: false },
  ];
  suppressed.state.magical_charm_suppressed = true;
  assert.equal(legal(suppressed), false, "Another source's Charmed cannot authorize this Kiss.");
  suppressed.state.timed_effects.push({
    effect_id: "charmed", source_id: actor.combatant_id, source_is_magical: false,
  });
  assert.equal(legal(suppressed), true, "A live owner-sourced Charmed permits Draining Kiss.");
} catch (error) {
  console.error("Browser Draining Kiss charmed-only regression failed.", error);
  throw error;
}

console.log("Browser Draining Kiss source-Charmed-only regressions passed.");
