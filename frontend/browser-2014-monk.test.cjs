"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

load("browser-heroes.js");
load("browser-condition-rules.js");
load("browser-condition-immunity.js");
load("browser-action-economy.js");
load("browser-timed-conditions.js");
load("browser-2014-monk.js");

const heroes = Object.values(window.IRON_PIT_BROWSER_HEROES);
const monk = (level) => heroes.find((hero) => hero.id === `kael-stillwater-2014-l${level}`);
for (let level = 1; level <= 10; level += 1) assert.ok(monk(level), `missing Monk level ${level}`);

assert.deepEqual(monk(1).ability_scores, { strength: 13, dexterity: 16, constitution: 14, intelligence: 11, wisdom: 15, charisma: 9 });
assert.equal(monk(1).armor_class, 15);
assert.equal(monk(4).armor_class, 16);
assert.equal(monk(8).armor_class, 17);
assert.equal(monk(1).speed_ft, 30);
assert.equal(monk(2).speed_ft, 40);
assert.equal(monk(6).speed_ft, 45);
assert.equal(monk(10).speed_ft, 50);
assert.equal(monk(4).attacks.find((attack) => attack.weaponId === "unarmed-strike").diceSize, 4);
assert.equal(monk(5).attacks.find((attack) => attack.weaponId === "unarmed-strike").diceSize, 6);
assert.equal(monk(2).resources.ki, 2);
assert.equal(monk(6).resources["wholeness-of-body"], 1);
assert.equal(monk(3).deflect_missiles, true);
assert.equal(monk(3).open_hand_technique, true);
assert.equal(monk(5).stunning_strike, true);
assert.equal(monk(7).evasion, true);
assert.deepEqual(monk(10).condition_immunities, ["poisoned"]);
assert.equal(monk(5).attack_action.slots.length, 2);
assert.equal(monk(6).healingActions[0].healingBonus, 18);
assert.deepEqual(monk(7).condition_removal_actions[0].removableConditions, ["charmed", "frightened"]);
assert.deepEqual(monk(10).weapon_masteries, []);
assert.ok(monk(10).attacks.every((attack) => attack.masteryProperty == null));

function state(template) {
  return {
    template, current_hp: template.max_hp || 20, temporary_hp: 0,
    active_effect_ids: [], active_buff_effect_ids: [], timed_effects: [],
    is_dead: false, is_unconscious: false, is_alive: true, turn_terminated: false,
    action_available: true, bonus_action_available: true, reaction_available: true,
    resources: { ...(template.resources || {}) },
  };
}

window.IRON_PIT_DICE = { roll: () => 4 };
const deflector = state(monk(3));
let result = window.IRON_PIT_BROWSER_MONK_2014.applyDeflectMissiles(
  deflector,
  { kind: "ranged" },
  [{ source: "arrow", total: 8 }],
);
assert.equal(result.used, true);
assert.equal(result.reduction, 10);
assert.equal(result.components[0].total, 0);
assert.equal(deflector.reaction_available, false);

window.IRON_PIT_BROWSER_SAVES = { resolveSavingThrow: () => ({ roll: { total: 1 }, succeeded: false }) };
const actor = { combatant_id: "kael", state: state(monk(5)) };
const target = { combatant_id: "target", state: state({ name: "Target", max_hp: 40, condition_immunities: [] }) };
result = window.IRON_PIT_BROWSER_MONK_2014.resolveStunning(
  1, 1, actor, target, monk(5).attacks.find((attack) => attack.weaponId === "unarmed-strike"),
);
assert.equal(result.save_dc, 13);
assert.equal(result.resource_remaining, 4);
assert.ok(target.state.active_effect_ids.includes("stunned"));
assert.equal(target.state.timed_effects[0].expiry_timing, "source_turn_end");
assert.equal(target.state.timed_effects[0].expires_round, 2);

const openActor = { combatant_id: "kael3", state: state(monk(3)) };
const openTarget = { combatant_id: "target2", state: state({ name: "Target 2", max_hp: 40, condition_immunities: [] }) };
result = window.IRON_PIT_BROWSER_MONK_2014.resolveOpenHand(1, 1, openActor, openTarget);
assert.equal(result.save_dc, 12);
assert.ok(openTarget.state.active_effect_ids.includes("prone"));

window.IRON_PIT_BROWSER_FORMATION = { targetOrder: (_member, setup) => setup.monsters };
window.IRON_PIT_BROWSER_STATE = { distance: () => 5 };
window.IRON_PIT_BROWSER_ATTACK = {
  resolveAttack: (sequence, round, member, victim, attack, _distance, options) => ({
    sequence, round_number: round, event_type: "attack", actor_id: member.combatant_id,
    actor_name: member.state.template.name, target_id: victim.combatant_id,
    target_name: victim.state.template.name, weapon_id: attack.weaponId, hit: true,
    feature_id: options.featureId, animation: "strike", description: "hit",
  }),
};
const flurryActor = { combatant_id: "kael2", state: state(monk(2)) };
const flurryTarget = { combatant_id: "dummy", state: state({ name: "Dummy", max_hp: 40, condition_immunities: [] }) };
result = window.IRON_PIT_BROWSER_MONK_2014.resolveBonus(
  2, 1, flurryActor, { heroes: [flurryActor], monsters: [flurryTarget] }, "1:kael2",
  [{ event_type: "attack", actor_id: "kael2", weapon_id: "unarmed-strike" }],
);
assert.equal(result.events.filter((event) => event.event_type === "attack").length, 2);
assert.ok(result.events.every((event) => event.feature_id === "flurry-of-blows"));
assert.equal(flurryActor.state.resources.ki, 1);
assert.equal(flurryActor.state.bonus_action_available, false);

console.log("2014 Open Hand Monk browser mechanics preserve progression, Ki, Flurry, Deflect Missiles, Stunning Strike, Open Hand Technique, and static defenses.");