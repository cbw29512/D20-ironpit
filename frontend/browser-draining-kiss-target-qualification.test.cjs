"use strict";

// Browser parity for the printed Draining Kiss target alternatives and scope.
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
  targetScope: "all-other-creatures",
  targetQualification: { anyOf: ["source_charmed", "willing"] },
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
  assert.equal(legal(ally), true);
  assert.equal(legal(actor), false, "all-other-creatures never includes the source itself");
  assert.equal(legal(ally, { ...action, targetScope: "enemies" }), false);
  assert.equal(legal(member("willing-enemy", "heroes", null)), false);
  const willingEnemy = member("willing-enemy", "heroes");
  willingEnemy.state.willing_attack_source_ids.push(actor.combatant_id);
  assert.equal(legal(willingEnemy), true);
  assert.equal(legal(willingEnemy, action, 10), false);

  const suppressed = member("suppressed-owner", "heroes");
  suppressed.state.active_effect_ids.push("charmed");
  suppressed.state.timed_effects = [
    { effect_id: "charmed", source_id: actor.combatant_id, source_is_magical: true },
    { effect_id: "charmed", source_id: "other-source", source_is_magical: false },
  ];
  suppressed.state.magical_charm_suppressed = true;
  assert.equal(legal(suppressed), false, "another source's Charmed cannot authorize this Kiss");
  suppressed.state.timed_effects.push({
    effect_id: "charmed", source_id: actor.combatant_id, source_is_magical: false,
  });
  assert.equal(legal(suppressed), true, "an unsuppressed owner-sourced Charmed does authorize it");
} catch (error) {
  console.error("Browser Draining Kiss target qualification regression failed.", error);
  throw error;
}

console.log("Browser Draining Kiss target qualification and scope regressions passed.");
