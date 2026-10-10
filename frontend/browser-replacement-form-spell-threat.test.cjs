"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

window.IRON_PIT_BROWSER_STATE = { distance: (a, b) => Math.abs(a.position_ft - b.position_ft) };
window.IRON_PIT_BROWSER_FORMATION = { weaponMeanDamage: () => 0 };
window.IRON_PIT_BROWSER_RESOURCES = { available: () => true };
window.IRON_PIT_BROWSER_CONDITION_RULES = {
  incapacitated: (state) => (state.active_effect_ids || []).includes("stunned"),
};
window.IRON_PIT_BROWSER_SPELL_POLICY_SUPPORT = {
  scaledSpell: (action, level) => ({ ...action, castLevel: level }),
};
window.IRON_PIT_BROWSER_OFFENSE_VALUE = {
  saveSpell: (_defender, action) => action.castLevel === 3 ? 13 : 5,
};
load("browser-replacement-form-spell-threat.js");
load("browser-replacement-form-threat.js");

const spell = { id: "save-spell", level: 3 };
const defender = {
  combatant_id: "defender", side: "heroes", position_ft: 0,
  state: { current_hp: 9, temporary_hp: 0 },
};
const enemy = {
  combatant_id: "enemy", side: "monsters", position_ft: 10,
  state: {
    is_alive: true, is_dead: false, current_hp: 33,
    action_available: false, bonus_action_available: false, turn_terminated: true,
    resources: { "spell-slot-3": 1 }, active_effect_ids: [],
    template: {
      speed_ft: 0, attacks: [], saving_throw_actions: [],
      spell_save_actions: [spell], spell_attack_actions: [],
      auto_hit_spell_actions: [], concentration_repeat_save_actions: [],
    },
  },
};
const setup = { heroes: [defender], monsters: [enemy] };
let incomingChoice = {
  action: spell, slotLevel: 3, targetIds: [defender.combatant_id],
  expectedDamage: 100, // Party-wide; not this defender's exposure.
};
window.IRON_PIT_BROWSER_SPELL_POLICY = {
  choose: (actor, given, key) => {
    assert.equal(given, setup);
    assert.equal(actor.state.action_available, true);
    assert.equal(actor.state.bonus_action_available, true);
    assert.equal(actor.state.turn_terminated, false);
    assert.equal(key, "forecast:enemy");
    return actor.state.resources["spell-slot-3"] ? incomingChoice : null;
  },
};
const spellThreat = window.IRON_PIT_BROWSER_REPLACEMENT_FORM_SPELL_THREAT;
const universal = window.IRON_PIT_BROWSER_REPLACEMENT_FORM_THREAT;
assert.equal(spellThreat.singleEnemy(enemy, defender, setup), 13);
assert.equal(universal.estimate(defender, setup), 13, "Spell damage joins the universal Action threat score");
assert.equal(enemy.state.action_available, false);
assert.equal(enemy.state.bonus_action_available, false);
assert.equal(enemy.state.turn_terminated, true);
assert.equal(enemy.state.resources["spell-slot-3"], 1, "Preview must never spend a slot");

incomingChoice = { ...incomingChoice, targetIds: ["other-hero"] };
assert.equal(spellThreat.singleEnemy(enemy, defender, setup), 0,
  "Do not score whole-party spell damage against a non-target");
incomingChoice = { ...incomingChoice, targetIds: [defender.combatant_id] };
enemy.state.resources["spell-slot-3"] = 0;
assert.equal(universal.estimate(defender, setup), 0, "Depleted resources make the spell unavailable");
enemy.state.resources["spell-slot-3"] = 1;

enemy.state.active_effect_ids.push("stunned");
assert.equal(universal.estimate(defender, setup), 0);
enemy.state.active_effect_ids.pop();
enemy.state.is_dead = true;
assert.equal(spellThreat.singleEnemy(enemy, defender, setup), 0);
enemy.state.is_dead = false;
window.IRON_PIT_BROWSER_SPELL_POLICY = { choose: () => null };
enemy.state.template.spell_save_actions = [];
enemy.state.template.spell_attack_actions = [{ id: "spell-attack" }];
enemy.state.template.auto_hit_spell_actions = [{ id: "auto-hit" }];
window.IRON_PIT_BROWSER_SPELL_ATTACK_POLICY = {
  choose: () => ({ target: { combatant_id: "other-hero" }, expectedDamage: 99 }),
};
window.IRON_PIT_BROWSER_AUTO_HIT_SPELL_POLICY = {
  choose: () => ({ target: defender, expectedDamage: 17 }),
};
assert.equal(spellThreat.singleEnemy(enemy, defender, setup), 17,
  "A spell targeted elsewhere cannot add its expected damage");
console.log("Incoming spell damage target/slot/state parity passed.");
