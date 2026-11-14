"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

window.IRON_PIT_ACTION_ECONOMY = {
  available: () => true, spend: () => {},
};
window.IRON_PIT_BROWSER_TIMED_SELF_BUFF_POLICY = { active: () => false };
window.IRON_PIT_BROWSER_ROLLS = {
  modeFromSources: (adv, dis) => adv && !dis ? "advantage" : dis && !adv ? "disadvantage" : "normal",
};
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_MODIFIERS = {
  removeSource: () => {}, d20TestAdvantage: () => 0,
};
load("browser-timed-conditions.js");
load("browser-timed-size-override.js");
load("browser-timed-condition-lifecycle.js");
load("browser-ability-checks.js");
load("browser-concentration.js");
load("browser-timed-self-buffs.js");
window.IRON_PIT_BROWSER_STATE = { effectiveMaxHp: (s) => s.template.max_hp };
window.IRON_PIT_BROWSER_HEALING_POLICY = { swarm: () => false };
load("browser-healing.js");

const original = { id: "renamed-fighter", name: "Renamed Fighter", size: "medium" };
const state = {
  template: original, active_effect_ids: [], active_modifiers: [],
  timed_effects: [], active_curses: [], replacement_form: null,
};
const member = { combatant_id: "fighter", side: "heroes", state };
const action = {
  id: "growth", name: "Growth", actionCost: "action",
  activationTiming: "action", durationRounds: 10,
  expiryTiming: "source_turn_start", conditionIds: [],
  abilityCheckAdvantageAbilities: ["strength"], sizeOverride: "large",
  savingThrowAdvantageGrants: [], modifierEffects: [],
};
try {
  const event = window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS.resolve(
    1, 1, member, action, { spendActionCost: false },
  );
  assert.equal(event.feature_id, "growth");
  assert.equal(original.size, "medium");
  assert.equal(state.template.size, "large");
  assert.equal(state.timed_effects[0].expires_round, 11);
  assert.equal(state.timed_effects[0].owned_previous_size, "medium");
  const mode = window.IRON_PIT_BROWSER_ABILITY_CHECKS.mode;
  assert.equal(mode(state, 0, 0, { ability: "strength" }), "advantage");
  assert.equal(mode(state, 0, 0, { ability: "dexterity" }), "normal");
  assert.equal(mode(state), "normal");
  assert.deepEqual(window.IRON_PIT_BROWSER_TIMED.removeGroup(state, state.timed_effects[0]), ["growth"]);
  assert.equal(state.template.size, "medium");
  assert.equal(mode(state, 0, 0, { ability: "strength" }), "normal");
  assert.equal(original.size, "medium");
  // Repeat with Concentration. On loss, the canonical effect cleanup must
  // restore the previous size so a future cast can enlarge again.
  const concentrating = { ...action, concentration: true };
  window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS.resolve(
    2, 2, member, concentrating, { spendActionCost: false },
  );
  assert.equal(state.template.size, "large");
  assert.equal(state.concentration.effect_id, "growth");
  assert.equal(window.IRON_PIT_BROWSER_CONCENTRATION.end(state, [state]), true);
  assert.equal(state.template.size, "medium");
  assert.deepEqual(state.timed_effects, []);
  assert.deepEqual(state.active_effect_ids, []);
  assert.equal(state.concentration, null);
  window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS.resolve(
    3, 3, member, concentrating, { spendActionCost: false },
  );
  assert.equal(state.template.size, "large");
  assert.equal(original.size, "medium");
  assert.equal(window.IRON_PIT_BROWSER_CONCENTRATION.end(state, [state]), true);
  assert.equal(state.template.size, "medium");
  // Full-HP source-owned expiry is the same generic size cleanup as
  // Concentration ending. Preserve unrelated effects and the original card.
  const fullHpAction = { ...action, id: "source-neutral-growth",
    name: "Source Neutral Growth", endsAtFullHp: true };
  state.template = { ...state.template, max_hp: 20,
    timed_self_buff_actions: [fullHpAction] };
  state.current_hp = 19;
  state.is_dead = false;
  const sourceSnapshot = JSON.stringify(state.template);
  window.IRON_PIT_BROWSER_TIMED.apply(state, "invisible", "external-source", {
    sourceEffectId: "independent-invisibility",
    useDefaultPoisonRecovery: false,
  });
  window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS.resolve(
    4, 4, member, fullHpAction, { spendActionCost: false },
  );
  assert.equal(state.template.size, "large");
  assert.equal(window.IRON_PIT_BROWSER_HEALING.restore(state, 1), 1);
  assert.equal(state.template.size, "medium");
  assert.ok(!state.active_effect_ids.includes(fullHpAction.id));
  assert.ok(state.active_effect_ids.includes("invisible"));
  assert.equal(state.timed_effects.length, 1);
  assert.equal(state.timed_effects[0].source_effect_id, "independent-invisibility");
  assert.equal(JSON.stringify(state.template), sourceSnapshot);
  console.log("Universal browser temporary size cleanup: group, Concentration and full HP passed.");
} catch (error) {
  console.error("Universal browser temporary size/check parity failed", error);
  throw error;
}
