"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-condition-rules.js", "browser-action-economy.js", "browser-rolls.js",
  "browser-tactical-mind.js", "browser-grapple.js", "browser-action-surge.js",
]) load(file);

const E = window.IRON_PIT_ACTION_ECONOMY;
const G = window.IRON_PIT_BROWSER_GRAPPLE;
const J = window.IRON_PIT_BROWSER_ACTION_SURGE;

function fighterState(actionSurge = 1) {
  return {
    template: {
      name: "Karnok Stoneward", archetype: "Fighter", level: 2, speed_ft: 30,
      skill_bonuses: { athletics: 5, acrobatics: 1 },
      attacks: [{ id: "greatsword", name: "Greatsword", kind: "melee", reach: 5 }],
    },
    current_hp: 20, is_dead: false, is_unconscious: false, is_alive: true,
    action_available: true, bonus_action_available: true, reaction_available: true,
    movement_remaining_ft: 30, active_effect_ids: [], grapple_sources: [], timed_effects: [],
    resources: { "second-wind": 2, "action-surge": actionSurge }, feature_last_turn_keys: {},
  };
}

{
  const state = fighterState(); E.spend(state, "action");
  const member = { combatant_id: "hero-1", side: "heroes", position_ft: 0, state };
  const event = J.use(1, 1, member, "1:hero-1");
  assert.equal(state.action_available, true);
  assert.equal(state.resources["action-surge"], 0);
  assert.equal(event.resource_remaining, 0);
}
{
  const state = fighterState(2); E.spend(state, "action");
  const member = { combatant_id: "hero-1", side: "heroes", position_ft: 0, state };
  J.use(1, 1, member, "1:hero-1"); E.spend(state, "action");
  assert.equal(J.available(state, "1:hero-1"), false, "Action Surge is once per turn");
  assert.equal(J.available(state, "2:hero-1"), true, "remaining use is legal on a later turn");
}

function grappleCheck(d10) {
  const state = fighterState();
  const member = { combatant_id: "hero-1", side: "heroes", position_ft: 0, state };
  G.apply(state, "monster-1", 15, 5, true);
  const queue = [5, d10];
  window.IRON_PIT_DICE = {
    roll: () => queue.shift(),
    rollMany: (count) => Array.from({ length: count }, () => queue.shift()),
  };
  const event = G.escape(1, 1, member);
  return { state, event };
}
{
  const { state, event } = grappleCheck(5);
  assert.equal(event.check_succeeded, true);
  assert.equal(event.ability_check_roll.total, 15);
  assert.match(event.description, /Tactical Mind/);
  assert.equal(state.resources["second-wind"], 1, "successful Tactical Mind spends Second Wind");
  assert.equal(state.grapple_sources.length, 0);
}
{
  const { state, event } = grappleCheck(1);
  assert.equal(event.check_succeeded, false);
  assert.equal(event.ability_check_roll.total, 11);
  assert.equal(state.resources["second-wind"], 2, "failed Tactical Mind retains Second Wind");
  assert.equal(state.grapple_sources.length, 1);
}

// Great Weapon Fighting must floor each weapon damage die independently, not the final total.
{
  const queue = [1, 2];
  window.IRON_PIT_DICE = {
    roll: () => queue.shift(),
    rollMany: (count) => Array.from({ length: count }, () => queue.shift()),
  };
  const attacker = { template: { traits: [] }, active_effect_ids: [], feature_last_turn_keys: {} };
  const attack = {
    name: "Greatsword", diceCount: 2, diceSize: 6, damageBonus: 4,
    damageType: "slashing", damageDieMinimum: 3, onHitDamage: [],
  };
  const damage = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(attacker, attack, false, "normal", "1:hero-1");
  assert.deepEqual(damage.roll.rolls, [3, 3]);
  assert.equal(damage.roll.total, 10);
}

// Browser attack rolls consume the compiled Archery bonus exactly once.
{
  const queue = [10, 10];
  window.IRON_PIT_DICE = {
    roll: () => queue.shift(),
    rollMany: (count) => Array.from({ length: count }, () => queue.shift()),
  };
  const baseRanged = window.IRON_PIT_BROWSER_ROLLS.d20(5, "normal");
  const archeryRanged = window.IRON_PIT_BROWSER_ROLLS.d20(7, "normal");
  assert.equal(baseRanged.total, 15);
  assert.equal(archeryRanged.total, 17);
  assert.equal(archeryRanged.modifier - baseRanged.modifier, 2);
}

// Prove the canonical turn finisher actually converts a spent Action into a second Attack.
window.IRON_PIT_BROWSER_STATE = {
  beginTurn: (state) => { state.action_available = true; state.bonus_action_available = true; state.movement_remaining_ft = 30; },
  nearestTarget: (_member, setup) => setup.monsters[0], distance: () => 5, packTactics: () => false,
};
window.IRON_PIT_BROWSER_GRAPPLE = { cleanup: () => {}, shouldEscape: () => false, speedIsZero: () => false };
window.IRON_PIT_BROWSER_SUPPORT = { resolve: (sequence) => ({ events: [], sequence }), secondWind: () => null, adrenaline: () => null };
window.IRON_PIT_BROWSER_RAGE = { enter: () => null, finalize: (sequence) => ({ event: null, sequence }) };
window.IRON_PIT_BROWSER_SPELL_POLICY = { choose: () => null };
window.IRON_PIT_BROWSER_SPELL_RESOLUTION = { resolve: () => { throw new Error("Magic must not be used by this test."); } };
window.IRON_PIT_BROWSER_CHARGE = { resolveClosing: (sequence) => ({ events: [], sequence, handled: false }), openingFeature: () => null };
window.IRON_PIT_BROWSER_FORMATION = { backlineHoldsPosition: () => false };
window.IRON_PIT_BROWSER_SAVES = { legalAction: () => false };
window.IRON_PIT_BROWSER_MULTIATTACK = { resolveAttackAction: () => { throw new Error("No Multiattack at Fighter 2."); } };
window.IRON_PIT_BROWSER_REACTION_MOVEMENT = { moveToward: (sequence) => ({ events: [], sequence, movement: null }) };
window.IRON_PIT_BROWSER_ATTACK = {
  resolveAttack: (sequence, round, member, target, attack, _distance, extra = {}) => {
    if (extra.spendAction !== false) E.spend(member.state, "action");
    return { sequence, round_number: round, event_type: "attack", actor_id: member.combatant_id,
      target_id: target.combatant_id, weapon_id: attack.id, feature_id: extra.featureId || null };
  },
};
load("browser-turn.js");
{
  const hero = { combatant_id: "hero-1", side: "heroes", position_ft: 0, state: fighterState() };
  const monster = { combatant_id: "monster-1", side: "monsters", position_ft: 5,
    state: { template: { name: "Target", kind: "monster" }, current_hp: 100, is_alive: true, is_dead: false, is_unconscious: false, grapple_sources: [] } };
  const result = window.IRON_PIT_BROWSER_TURN.resolveTurn(1, 1, hero, { heroes: [hero], monsters: [monster] });
  assert.equal(result.events.filter((event) => event.event_type === "attack").length, 2);
  assert.equal(result.events.filter((event) => event.feature_id === "action-surge").length, 2);
  assert.equal(hero.state.resources["action-surge"], 0);
}

console.log("Browser Fighter 2 progression regressions passed.");
