"use strict";

// One reusable browser self-buff implementation: source data alone changes
// charge count, expiry predicates, and the one-hour concentration lifetime.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_MODIFIERS = { removeSource: () => {} };
load("browser-action-economy.js");
load("browser-condition-rules.js");
load("browser-timed-conditions.js");
load("browser-timed-condition-lifecycle.js");
load("browser-concentration.js");
load("browser-spellcasting.js");
load("browser-timed-self-buff-policy.js");
load("browser-timed-self-buffs.js");

const invis = {
  id: "invisibility", name: "Invisibility", actionCost: "action",
  conditionIds: ["invisible"], concentration: true, magicalEffect: true,
  endsOnOwnerAttack: true, endsOnOwnerSpellCast: true,
  endsOnOwnerActionIds: ["enlarge"], durationRounds: 600,
  expiryTiming: "source_turn_end", priority: 70,
  resourceId: "invisibility", resourceCost: 1, animation: "invisibility",
};
// Synthetic generic self-action represents the owner-event lifecycle;
// implementing actual Enlarge's dice/Strength clauses is a separate family.
const namedAction = {
  id: "enlarge", name: "Renamed Buff", actionCost: "action",
  damageResistances: ["cold"], durationRounds: 1,
  expiryTiming: "source_turn_end",
};
function makeState(id) {
  return {
    template: {
      id, name: id, ruleset: "2014", armor_class: 16,
      timed_self_buff_actions: [invis, namedAction], innate_condition_ids: [],
      condition_immunities: [], damage_resistances: [],
    },
    current_hp: 26, is_alive: true, is_dead: false, is_unconscious: false,
    action_available: true, bonus_action_available: true,
    reaction_available: true, opening_buff_id: null,
    resources: { invisibility: 1 }, timed_effects: [], active_effect_ids: [],
    active_modifiers: [], temporary_damage_resistances: [],
  };
}
function verify() {
  try {
    const state = makeState("other-renamed-source");
    const owner = { combatant_id: "owner", side: "monsters", state };
    const opts = { spendActionCost: false, affectedStates: [state] };
    window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS.resolve(1, 1, owner, invis, opts);
    assert.equal(state.resources.invisibility, 0, "rest recharge spent once");
    assert.equal(state.concentration.effect_id, "invisibility");
    assert.equal(state.concentration.expires_round, 601);
    assert.ok(state.active_effect_ids.includes("invisible"));
    assert.equal(state.timed_effects[0].ends_on_owner_spell_cast, true);
    assert.deepEqual(state.timed_effects[0].ends_on_owner_action_ids, ["enlarge"]);

    // Unrelated Actions do not trigger the source-declared name condition.
    assert.deepEqual(window.IRON_PIT_BROWSER_TIMED.expireOnOwnerEvent(
      state, "action", [state], "other",
    ), []);
    assert.ok(state.active_effect_ids.includes("invisible"));

    // Using another self-buff with the declared ID triggers universal expiry.
    window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS.resolve(2, 1, owner, namedAction, opts);
    assert.equal(state.concentration, null);
    assert.ok(!state.active_effect_ids.includes("invisible"));
    assert.equal(state.resources.invisibility, 0);
    assert.throws(() => window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS.resolve(
      3, 1, owner, invis, opts,
    ), /resource is unavailable/);
  } catch (error) {
    console.error("Browser rest-charge Invisibility / named Action regression failed", error);
    throw error;
  }
}
verify();
console.log("2014 rest-charge Invisibility reuses shared browser runtime.");
