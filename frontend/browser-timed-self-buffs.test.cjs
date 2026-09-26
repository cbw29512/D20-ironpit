"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
load("browser-action-economy.js");
load("browser-condition-rules.js");
load("browser-timed-conditions.js");
load("browser-timed-self-buffs.js");
load("browser-precombat-buffs.js");
load("browser-attack.js");

const damageTypes = [
  "acid", "bludgeoning", "cold", "fire", "lightning", "necrotic",
  "piercing", "poison", "psychic", "radiant", "slashing", "thunder",
];

function state(name) {
  return {
    template: {
      name, ruleset: "2014", armor_class: 15, damage_resistances: [],
      damage_immunities: [], damage_vulnerabilities: [], condition_immunities: [],
    },
    current_hp: 50, is_alive: true, is_dead: false, is_unconscious: false,
    action_available: true, bonus_action_available: true, reaction_available: true,
    active_effect_ids: [], timed_effects: [], temporary_damage_resistances: [],
    resources: { ki: 18 },
  };
}

const monk = { combatant_id: "kael", side: "heroes", state: state("Kael") };
const target = { combatant_id: "target", side: "monsters", state: state("Target") };
const action = {
  id: "empty-body", name: "Empty Body", actionCost: "action",
  resourceId: "ki", resourceCost: 4, durationRounds: 10,
  conditionIds: ["invisible"], damageResistances: damageTypes,
  expiryTiming: "source_turn_start", priority: 100, animation: "empty-body",
};
monk.state.template.timed_self_buff_actions = [action];
target.state.template.timed_self_buff_actions = [];

assert.equal(window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS.choose(monk).id, "empty-body");
const event = window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS.resolve(1, 1, monk, action);
assert.equal(event.feature_id, "empty-body");
assert.equal(event.resource_remaining, 14);
assert.equal(monk.state.action_available, false);
assert.ok(monk.state.active_effect_ids.includes("invisible"));
assert.equal(monk.state.timed_effects[0].expires_round, 11);
assert.equal(window.IRON_PIT_BROWSER_ATTACK.adjustedDamage(monk.state, 9, "fire"), 4);
assert.equal(window.IRON_PIT_BROWSER_ATTACK.adjustedDamage(monk.state, 9, "force"), 9);

const fromInvisible = window.IRON_PIT_BROWSER_ATTACK.conditionSources(monk.state, target.state, 5, "target");
const againstInvisible = window.IRON_PIT_BROWSER_ATTACK.conditionSources(target.state, monk.state, 5, "kael");
assert.ok(fromInvisible.advantage >= 1);
assert.ok(againstInvisible.disadvantage >= 1);

const setup = { heroes: [monk], monsters: [target] };
const expired = window.IRON_PIT_BROWSER_TIMED.expireSourceStart(2, 11, monk, setup);
assert.equal(expired.events[0].feature_id, "empty-body");
assert.ok(!monk.state.active_effect_ids.includes("invisible"));
assert.equal(window.IRON_PIT_BROWSER_ATTACK.adjustedDamage(monk.state, 9, "fire"), 9);

const countercharm = {
  id: "countercharm", name: "Countercharm", actionCost: "action",
  resourceId: null, resourceCost: 1, durationRounds: 1,
  conditionIds: [], damageResistances: [], expiryTiming: "source_turn_end",
  priority: 5, animation: "countercharm",
  friendlySaveAdvantageAura: {
    radius_ft: 30,
    required_effect_tags: ["charmed", "frightened"],
    requires_hearing: true,
  },
};
const bard = { combatant_id: "bard", side: "heroes", position_ft: 0, state: state("Bard") };
const ally = { combatant_id: "ally", side: "heroes", position_ft: 20, state: state("Ally") };
const charmTarget = { combatant_id: "charm-target", side: "monsters", position_ft: 40, state: state("Charm Target") };
bard.state.template.timed_self_buff_actions = [countercharm];
ally.state.template.timed_self_buff_actions = [];
charmTarget.state.template.timed_self_buff_actions = [];
const charmSetup = { heroes: [bard, ally], monsters: [charmTarget] };
window.IRON_PIT_BROWSER_STATE = {
  distance: (a, b) => Math.abs((a.position_ft || 0) - (b.position_ft || 0)),
  effectiveMaxHp: (s) => s.template.max_hp || 50,
};
assert.equal(window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS.choose(bard, charmSetup), null);
ally.state.active_effect_ids = ["charmed"];
assert.equal(window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS.choose(bard, charmSetup).id, "countercharm");

const openingBard = { combatant_id: "opening-bard", side: "heroes", position_ft: 0, state: state("Opening Bard") };
const openingAlly = { combatant_id: "opening-ally", side: "heroes", position_ft: 20, state: state("Opening Ally") };
const openingEnemy = { combatant_id: "opening-enemy", side: "monsters", position_ft: 40, state: state("Opening Enemy") };
openingBard.state.template.timed_self_buff_actions = [countercharm];
openingAlly.state.template.timed_self_buff_actions = [];
openingEnemy.state.template.timed_self_buff_actions = [];
const openingSetup = { heroes: [openingBard, openingAlly], monsters: [openingEnemy] };
const openingPrep = window.IRON_PIT_BROWSER_PRECOMBAT_BUFFS.prepare(openingSetup, 1);
assert.equal(openingPrep.events.length, 1);
assert.equal(openingPrep.events[0].feature_id, "countercharm");
assert.equal(openingPrep.events[0].round_number, 0);
assert.equal(openingBard.state.opening_buff_id, "countercharm");
assert.equal(openingBard.state.action_available, true);
assert.equal(openingBard.state.timed_effects[0].expires_round, 1);
assert.match(openingPrep.events[0].description, /free opening buff/);

const lowKi = { combatant_id: "low", side: "heroes", state: state("Low Ki") };
lowKi.state.template.timed_self_buff_actions = [action];
lowKi.state.resources.ki = 3;
assert.equal(window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS.choose(lowKi), null);
assert.throws(() => window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS.resolve(1, 1, lowKi, action), /resource is unavailable/);
assert.equal(lowKi.state.action_available, true);
assert.equal(lowKi.state.resources.ki, 3);


window.IRON_PIT_BROWSER_HEALING = { chooseAction: () => null };
window.IRON_PIT_BROWSER_CONDITION_REMOVAL = { chooseAction: () => null };
window.IRON_PIT_BROWSER_EFFECT_REMOVAL = { choose: () => null };
window.IRON_PIT_BROWSER_CLERIC_CHANNEL = { resolve: () => null };
window.IRON_PIT_BROWSER_PALADIN_2014 = { resolveChannel: () => null };
window.IRON_PIT_BROWSER_STATE = {
  distance: (a, b) => Math.abs((a.position_ft || 0) - (b.position_ft || 0)),
  effectiveMaxHp: (s) => s.template.max_hp || 50,
};
load("browser-support.js");

const supportMonk = { combatant_id: "support-kael", side: "heroes", state: state("Support Kael") };
supportMonk.state.template.timed_self_buff_actions = [action];
const supportTarget = { combatant_id: "support-target", side: "monsters", state: state("Support Target") };
supportTarget.state.template.timed_self_buff_actions = [];
const supportResult = window.IRON_PIT_BROWSER_SUPPORT.resolve(
  1, 1, supportMonk, { heroes: [supportMonk], monsters: [supportTarget] }, "1:support-kael",
);
assert.deepEqual(supportResult.events.map((item) => item.feature_id), ["empty-body"]);
assert.equal(supportResult.sequence, 2);
assert.equal(supportMonk.state.action_available, false);
assert.equal(supportMonk.state.resources.ki, 14);
assert.ok(supportMonk.state.active_effect_ids.includes("invisible"));

console.log("Browser timed self-buff, invisibility, and owned resistance parity are certified.");
