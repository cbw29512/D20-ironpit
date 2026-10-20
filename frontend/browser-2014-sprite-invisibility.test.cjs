"use strict";

// Source-neutral browser proof: Sprite's card fields are the same fields
// usable by any combatant's opening Invisible self-buff.
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
load("browser-concentration.js");
load("browser-spellcasting.js");
load("browser-timed-self-buff-policy.js");
load("browser-timed-self-buffs.js");
load("browser-precombat-buffs.js");

const action = {
  id: "invisibility", name: "Invisibility", actionCost: "action",
  conditionIds: ["invisible"], concentration: true, magicalEffect: true,
  endsOnOwnerAttack: true, endsOnOwnerSpellCast: true,
  durationRounds: null, expiryTiming: null, priority: 70,
  resourceId: null, animation: "invisibility",
};
function state(name, actions = []) {
  return {
    template: {
      id: name, name, ruleset: "2014", armor_class: 15,
      timed_self_buff_actions: actions, innate_condition_ids: [],
      condition_immunities: [], damage_resistances: [],
    },
    current_hp: 10, is_alive: true, is_dead: false, is_unconscious: false,
    action_available: true, bonus_action_available: true,
    reaction_available: true, opening_buff_id: null,
    resources: {}, timed_effects: [], active_effect_ids: [],
    active_modifiers: [], temporary_damage_resistances: [],
  };
}
const sprite = { combatant_id: "sprite", side: "monsters", state: state("Sprite", [action]) };
const hero = { combatant_id: "hero", side: "heroes", state: state("Hero") };
const setup = { heroes: [hero], monsters: [sprite] };
const initial = window.IRON_PIT_BROWSER_PRECOMBAT_BUFFS.prepare(setup);
assert.equal(initial.events.length, 1);
assert.equal(initial.events[0].round_number, 0);
assert.equal(initial.events[0].feature_id, "invisibility");
assert.match(initial.events[0].description, /free opening buff/);
assert.equal(sprite.state.action_available, true, "opening buff consumes no combat Action");
assert.equal(sprite.state.opening_buff_id, "invisibility");
assert.ok(sprite.state.active_effect_ids.includes("invisible"));
assert.equal(sprite.state.concentration.effect_id, "invisibility");
assert.equal(sprite.state.concentration.expires_round, null);
assert.equal(sprite.state.timed_effects[0].ends_on_owner_attack, true);
assert.equal(sprite.state.timed_effects[0].ends_on_owner_spell_cast, true);
assert.equal(sprite.state.timed_effects[0].source_is_magical, true);
assert.equal(sprite.state.timed_effects[0].expires_round, null);
assert.equal(window.IRON_PIT_BROWSER_PRECOMBAT_BUFFS.prepare(setup).events.length, 0);

const expiredByAttack = window.IRON_PIT_BROWSER_TIMED.expireOnOwnerEvent(
  sprite.state, "attack", [sprite.state, hero.state],
);
assert.deepEqual(expiredByAttack, ["invisible"]);
assert.equal(sprite.state.concentration, null);
assert.ok(!sprite.state.active_effect_ids.includes("invisible"));
assert.equal(window.IRON_PIT_BROWSER_TIMED.expireOnOwnerEvent(sprite.state, "attack").length, 0);

const renamed = { ...action, id: "renamed-shroud", name: "Shroud of Smoke" };
const second = { combatant_id: "second", side: "heroes", state: state("Other", [renamed]) };
const otherSetup = { heroes: [second], monsters: [hero] };
const opened = window.IRON_PIT_BROWSER_PRECOMBAT_BUFFS.prepare(otherSetup);
assert.equal(opened.events.length, 1);
assert.equal(second.state.opening_buff_id, "renamed-shroud");
assert.ok(second.state.active_effect_ids.includes("invisible"));
window.IRON_PIT_BROWSER_SPELLCASTING.markSlotSpellCast(second.state, "1:second");
assert.equal(second.state.concentration, null, "spell-cast expiry ends concentration");
assert.ok(!second.state.active_effect_ids.includes("invisible"));
assert.equal(second.state.spell_slot_expended_turn_key, "1:second");

const fresh = state("Sprite", [action]);
assert.equal(fresh.concentration, undefined);
assert.deepEqual(fresh.active_effect_ids, []);
assert.deepEqual(fresh.timed_effects, []);

console.log("2014 Sprite pre-initiative Invisible buff and generic action expiry passed.");
