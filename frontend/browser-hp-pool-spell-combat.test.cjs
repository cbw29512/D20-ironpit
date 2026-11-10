"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
for (const module of [
  "browser-condition-immunity.js", "browser-condition-rules.js",
  "browser-action-economy.js", "browser-state.js", "browser-timed-conditions.js",
  "browser-source-bound-effects.js", "browser-spellcasting.js",
  "browser-spell-area.js", "browser-spell-policy-support.js",
  "browser-hit-point-pool.js", "browser-hp-pool-spell-policy.js",
  "browser-hp-pool-spell-resolution.js", "browser-spell-offense.js",
  "browser-formation.js",
]) load(module);

const S = window.IRON_PIT_BROWSER_STATE;
const C = window.IRON_PIT_BROWSER_CONDITION_RULES;
const P = window.IRON_PIT_BROWSER_HP_POOL_SPELL_POLICY;
const R = window.IRON_PIT_BROWSER_HP_POOL_SPELL;
const F = window.IRON_PIT_BROWSER_FORMATION;
const SO = window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS;
const sleep = {
  id: "sleep", name: "Sleep", level: 1, actionCost: "action", range: 90,
  areaRadius: 20, poolDiceCount: 5, poolDiceSize: 8,
  extraDicePerUpcastLevel: 2, conditionId: "unconscious",
  durationRounds: 10, expiryTiming: "source_turn_start",
  excludedCreatureTypes: ["undead"], excludedConditionImmunities: ["charmed"],
  skipUnconscious: true, endsOnDamage: true,
  allowedRemovalActionIds: ["wake-sleeper"], animation: "sleep",
};
function member(id, side, hp, actions = [], resources = {}, alternate = []) {
  const template = {
    id, name: id, kind: side === "heroes" ? "character" : "monster",
    ruleset: "2014", creature_type: "humanoid", condition_immunities: [],
    max_hp: hp, speed_ft: 30, size: "medium",
    movement_modes: { walk_ft: 30, fly_ft: 0, climb_ft: 0, swim_ft: 0, burrow_ft: 0, hover: false },
    attacks: [], primary_attack_id: null, resources,
    hit_point_pool_spell_actions: actions, alternate_spell_cast_grants: alternate,
  };
  return { combatant_id: id, side, position_ft: side === "monsters" ? 0 : 30,
    state: S.buildState(template) };
}
const grant = { source_id: "sleep", source_name: "Sleep",
  spell_id: "sleep", cast_level: 1, resource_id: "sleep",
  resource_cost: 1, priority: 0 };
const caster = member("synthetic caster", "monsters", 40, [sleep], { sleep: 2 }, [grant]);
const low = member("low HP", "heroes", 2);
const high = member("high HP", "heroes", 8);
const setup = { monsters: [caster], heroes: [high, low] };
const immutableSpell = JSON.stringify(sleep);
const choice = P.choose(caster, setup, "1:caster");
assert.ok(choice, "generic HP-pool caster must discover Sleep");
assert.equal(choice.action, sleep);
assert.equal(choice.alternateCast.resource_id, "sleep");

// Five 1s roll only 5 HP: lowest HP target falls asleep, higher HP remains awake.
window.IRON_PIT_DICE = { rollMany: (count) => Array(count).fill(1) };
const result = R.resolve(1, 1, caster, setup, choice, "1:caster");
assert.equal(result.events[0].feature_roll.total, 5);
assert.equal(caster.state.action_available, false);
assert.equal(caster.state.resources.sleep, 1);
assert.equal(caster.state.spell_slot_expended_turn_key, null);
assert.deepEqual(result.events.filter(event => event.target_id).map(event => event.target_id), ["low HP"]);
assert.ok(C.has(low.state, "unconscious"));
assert.ok(!C.has(high.state, "unconscious"));
assert.deepEqual(F.targetOrder(caster, setup).map(m => m.combatant_id), ["high HP"],
  "awake target must be preferred over an Incapacitated target");
high.state.active_effect_ids.push("stunned");
assert.equal(S.targetPriority(low), 2, "damage-waking Sleep has lower priority");
assert.equal(S.targetPriority(high), 1, "non-sleep Incapacitated remains targetable first");
high.state.active_effect_ids = high.state.active_effect_ids.filter(id => id !== "stunned");
assert.equal(low.state.current_hp, 2, "Sleep never deals HP damage");
assert.equal(low.state.timed_effects[0].ends_on_damage, true);
assert.equal(low.state.timed_effects[0].expires_round, 11);
assert.deepEqual(low.state.timed_effects[0].allowed_removal_action_ids, ["wake-sleeper"]);
assert.equal(JSON.stringify(sleep), immutableSpell);

caster.state.action_available = true;
high.state.current_hp = 1;
const next = P.choose(caster, setup, "2:caster");
assert.ok(next);
const second = R.resolve(1, 2, caster, setup, next, "2:caster");
assert.equal(second.events[0].feature_id, "sleep");
assert.equal(caster.state.resources.sleep, 0);
assert.ok(C.has(high.state, "unconscious"));
assert.deepEqual(F.targetOrder(caster, setup).map(m => m.combatant_id), ["high HP", "low HP"],
  "all sleeping enemies must remain selectable for ordinary attacks");

const removed = SO.endDamageSensitive(high.state);
assert.ok(removed.includes("unconscious"), "damage triggers shared wake-up lifecycle");
assert.ok(!C.has(high.state, "unconscious"));
assert.deepEqual(F.targetOrder(caster, setup).map(m => m.combatant_id), ["high HP"]);
assert.equal(P.choose(caster, setup, "3:caster"), null, "innate daily uses are exhausted");

const undead = member("undead", "heroes", 3);
undead.state.template.creature_type = "undead";
assert.equal(P.eligible(caster, undead, sleep, setup), false);
const charmedImmune = member("charm immune", "heroes", 3);
charmedImmune.state.template.condition_immunities = ["charmed"];
assert.equal(P.eligible(caster, charmedImmune, sleep, setup), false);
assert.equal(P.eligible(caster, low, sleep, setup), false, "already-unconscious target skipped");

assert.ok(window.IRON_PIT_BROWSER_SPELL_OFFENSE.choose(member("control", "monsters", 10,
  [sleep], { sleep: 1 }, [grant]), { monsters: [], heroes: [member("enemy", "heroes", 3)] },
  "1:control"), "generic HP-pool spell must participate in normal spell choice");

const preparedCaster = member("prepared caster", "monsters", 25, [sleep], { "spell-slot-2": 1 });
const preparedTarget = member("prepared target", "heroes", 4);
const preparedSetup = { monsters: [preparedCaster], heroes: [preparedTarget] };
const preparedChoice = P.choose(preparedCaster, preparedSetup, "1:prepared");
assert.ok(preparedChoice, "prepared Sleep uses ordinary spell slots");
assert.equal(preparedChoice.slotLevel, 2);
assert.equal(preparedChoice.alternateCast, null);
const preparedResult = R.resolve(1, 1, preparedCaster, preparedSetup, preparedChoice, "1:prepared");
assert.equal(preparedResult.events[0].feature_roll.rolls.length, 7,
  "2014 upcast adds exactly two d8 for one higher slot");
assert.equal(preparedCaster.state.resources["spell-slot-2"], 0);
assert.equal(preparedCaster.state.spell_slot_expended_turn_key, "1:prepared");
assert.ok(C.has(preparedTarget.state, "unconscious"));

const immuneCaster = member("immune cluster caster", "monsters", 40, [sleep], { sleep: 1 }, [grant]);
const clustered = Array.from({ length: 6 }, (_, i) => member(`cluster-${i}`, "heroes", 4));
clustered.slice(0, 5).forEach(target => { target.state.template.creature_type = "undead"; });
const clusterSetup = { monsters: [immuneCaster], heroes: clustered };
const clusterChoice = P.choose(immuneCaster, clusterSetup, "1:immune-caster");
assert.ok(clusterChoice, "Sleep must still cast when the largest cluster is immune");
assert.ok(clusterChoice.placement.enemyIds.includes("cluster-5"));
assert.ok(!clusterChoice.placement.enemyIds.includes("cluster-0"));
R.resolve(1, 1, immuneCaster, clusterSetup, clusterChoice, "1:immune-caster");
assert.ok(C.has(clustered[5].state, "unconscious"));
assert.ok(clustered.slice(0, 5).every(target => !C.has(target.state, "unconscious")));

console.log("2014 Sleep browser live casting, resource, wake and awake-first targeting parity passed.");
