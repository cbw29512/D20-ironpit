"use strict";

// Shared save target gate: the active condition must belong to this actor.
// The printed action name is irrelevant to eligibility and combat resolution.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
window.IRON_PIT_BROWSER_CONDITION_RULES = {
  has: (state, id) => (state.active_effect_ids || []).includes(id),
  canSee: () => true,
};
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = {
  immune: (state, id, _source, options = {}) => Boolean(
    id === "charmed"
    && options.sourceIsMagical
    && state.magical_charm_suppressed
  ),
};
window.IRON_PIT_BROWSER_STATE = {
  sizeAtMost: () => true,
  distance: () => 5,
};
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-save-action-support.js"), "utf8"),
  { filename: "browser-save-action-support.js" },
);

function member(id, sourceId = null) {
  const effects = sourceId ? [{
    effect_id: "charmed", source_id: sourceId, source_effect_id: "renamed-control",
  }] : [];
  return {
    combatant_id: id,
    state: {
      template: { creature_type: "humanoid", name: id },
      active_effect_ids: sourceId ? ["charmed"] : [],
      timed_effects: effects, grapple_sources: [],
      current_hp: 80, is_alive: true, is_dead: false,
    },
  };
}
const actor = member("owner");
const action = {
  id: "unrelated-action", name: "Renamed Source Action",
  requiredTargetSourceCondition: "charmed",
  range: 5, requiresTargetSight: false,
};
const allowed = (target, sourceId = actor.combatant_id, distance = 5) =>
  window.IRON_PIT_BROWSER_SAVE_ACTION_SUPPORT.legalAction(
    action, target, distance, sourceId, actor,
  );

try {
  assert.equal(allowed(member("uncharmed")), false);
  assert.equal(allowed(member("other-charmer", "someone-else")), false);
  const owned = member("owned", actor.combatant_id);
  assert.equal(allowed(owned), true);
  assert.equal(allowed(owned, "different-caster"), false);
  assert.equal(allowed(owned, actor.combatant_id, 10), false);
  owned.state.active_effect_ids = []; // An immunity/counter can suppress Charmed.
  assert.equal(allowed(owned), false);
  owned.state.active_effect_ids = ["charmed"];

  // Another live owner condition must not broaden the gate for this source.
  owned.state.timed_effects = [{
    effect_id: "frightened", source_id: actor.combatant_id,
    source_effect_id: "unrelated-effect",
  }];
  assert.equal(allowed(owned), false);
  owned.state.timed_effects = [{
    effect_id: "charmed", source_id: actor.combatant_id,
    source_effect_id: "renamed-effect",
  }];
  assert.equal(allowed(owned), true);

  // An active different-source Charmed cannot authorize a suppressed
  // owner-sourced magical Charmed. Countering is per timed-effect instance.
  owned.state.timed_effects = [
    { effect_id: "charmed", source_id: actor.combatant_id, source_is_magical: true },
    { effect_id: "charmed", source_id: "other-charmer", source_is_magical: false },
  ];
  owned.state.magical_charm_suppressed = true;
  assert.equal(allowed(owned), false);
  owned.state.timed_effects.push({
    effect_id: "charmed", source_id: actor.combatant_id, source_is_magical: false,
  });
  assert.equal(allowed(owned), true);

  // A normal save Action is unchanged by the optional source-owned parameter.
  const plain = { id: "normal", name: "Normal", range: 5 };
  assert.equal(window.IRON_PIT_BROWSER_SAVE_ACTION_SUPPORT.legalAction(
    plain, member("uncharmed"), 5, actor.combatant_id, actor,
  ), true);
} catch (error) {
  console.error("Browser owner-condition target eligibility regression failed.", error);
  throw error;
}

console.log("Browser universal source-owned condition target regressions passed.");
