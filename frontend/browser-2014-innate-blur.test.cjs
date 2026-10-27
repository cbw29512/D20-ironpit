"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
for (const file of [
  "browser-monsters-2014.js", "browser-modifier-validation.js", "browser-modifiers.js",
  "browser-action-economy.js", "browser-timed-conditions.js", "browser-concentration.js",
  "browser-spell-modifiers.js", "browser-timed-self-buff-policy.js",
  "browser-timed-self-buffs.js", "browser-effective-senses.js",
  "browser-defensive-modifier-rules.js",
]) load(file);

const template = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-steam-mephit"];
assert.ok(template, "Steam Mephit must be source-admitted after complete innate Blur binding");
const blur = template.timed_self_buff_actions.find((item) => item.id === "blur");
assert.ok(blur);
assert.equal(blur.actionCost, "action");
assert.equal(blur.resourceId, "blur");
assert.equal(blur.resourceCost, 1);
assert.equal(blur.durationRounds, 10);
assert.equal(blur.expiryTiming, "source_turn_start");
assert.equal(blur.magicalEffect, true);
assert.equal(blur.concentration, true);
assert.deepEqual(blur.modifierEffects, [{
  kind: "attacks-against-disadvantage",
  flatBonus: 0,
  diceCount: 0,
  diceSize: 0,
  damageType: null,
  bypassAttackerSenses: ["blindsight", "truesight"],
}]);
assert.equal(template.resources.blur, 1);

function freshState() {
  return {
    template, resources: { ...template.resources }, current_hp: template.max_hp,
    is_alive: true, is_dead: false, is_unconscious: false,
    action_available: true, bonus_action_available: true, reaction_available: true,
    active_effect_ids: [], active_modifiers: [], timed_effects: [], concentration: null,
    voluntary_turn_activity: null, delayed_resource_refills: [],
  };
}

const state = freshState();
const member = { combatant_id: "steam-mephit", side: "monsters", state };
const runtime = window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS;
assert.equal(window.IRON_PIT_BROWSER_TIMED_SELF_BUFF_POLICY.concentrationGrantOnly(blur), false);
assert.equal(runtime.choose(member).id, "blur");
const event = runtime.resolve(1, 1, member, blur, { affectedStates: [state] });
assert.equal(event.feature_id, "blur");
assert.equal(event.resource_remaining, 0);
assert.equal(state.action_available, false);
assert.equal(state.concentration.effect_id, "blur");
assert.equal(state.timed_effects[0].source_effect_id, "blur");
assert.equal(state.active_modifiers[0].kind, "attacks-against-disadvantage");

const defense = window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS;
assert.equal(defense.attacksAgainstDisadvantage(state, { blindsight_ft: 0, truesight_ft: 0 }, 5), 1);
assert.equal(defense.attacksAgainstDisadvantage(state, { blindsight_ft: 0, truesight_ft: 30 }, 5), 0);
window.IRON_PIT_BROWSER_CONCENTRATION.end(state, [state]);
assert.equal(state.concentration, null);
assert.equal(state.active_modifiers.length, 0);
assert.equal(state.timed_effects.length, 0);

const nextFight = freshState();
assert.equal(nextFight.resources.blur, 1);
assert.equal(nextFight.concentration, null);
assert.equal(nextFight.active_modifiers.length, 0);

console.log("2014 innate Blur binding, browser resolution, senses, and fresh-fight reset passed.");
