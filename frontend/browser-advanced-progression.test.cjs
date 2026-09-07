"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

window.IRON_PIT_BROWSER_STATE = { effectiveMaxHp: (state) => state.template.max_hp };
load("browser-turn.js");

// Survivor: Advantage on Death Saves and 18-20 produces the natural-20 recovery result.
{
  const queue = [5, 18];
  window.IRON_PIT_DICE = { roll: () => queue.shift() };
  const state = {
    template: { name: "Karnok", survivor_death_save_advantage: true, survivor_death_save_critical_minimum: 18 },
    current_hp: 0, is_alive: true, is_dead: false, is_unconscious: true, is_stable: false,
    death_save_successes: 1, death_save_failures: 1,
  };
  const event = window.IRON_PIT_BROWSER_TURN.deathSave(1, 1, { combatant_id: "hero-1", state });
  assert.deepEqual(event.death_save_roll.rolls, [5, 18]);
  assert.equal(event.death_save_roll.mode, "advantage");
  assert.equal(event.death_save_roll.selected_roll, 18);
  assert.equal(state.current_hp, 1);
  assert.equal(state.death_save_successes, 0);
  assert.equal(state.death_save_failures, 0);
}

// Heroic Rally: only a living Bloodied character heals, for 5 + Constitution modifier.
{
  const state = {
    template: { name: "Karnok", max_hp: 100, bloodied_start_turn_healing_bonus: 5, ability_scores: { constitution: 20 } },
    current_hp: 50, is_alive: true, is_dead: false,
  };
  const member = { combatant_id: "hero-1", state };
  const event = window.IRON_PIT_BROWSER_TURN.progressionHealing(1, 1, member);
  assert.equal(state.current_hp, 60);
  assert.equal(event.hp_before, 50);
  assert.equal(event.hp_after, 60);
  state.current_hp = 51;
  assert.equal(window.IRON_PIT_BROWSER_TURN.progressionHealing(2, 2, member), null);
}

// Steady Aim: spends the Bonus Action and contributes exactly one Advantage source.
{
  let capturedAdvantage = null;
  window.IRON_PIT_ACTION_ECONOMY = {
    available: (state, cost) => cost === "action" ? state.action_available : cost === "bonus_action" ? state.bonus_action_available : state.reaction_available,
    spend: (state, cost) => { if (cost === "action") state.action_available = false; else if (cost === "bonus_action") state.bonus_action_available = false; else state.reaction_available = false; },
  };
  window.IRON_PIT_BROWSER_STATE = {
    effectiveMaxHp: (state) => state.template.max_hp,
    beginTurn: (state) => { state.action_available = true; state.bonus_action_available = true; },
    packTactics: () => false,
  };
  window.IRON_PIT_BROWSER_GRAPPLE = { cleanup: () => {}, shouldEscape: () => false };
  window.IRON_PIT_BROWSER_ONGOING_SPELL_CONTROL = { forcedRetreatActive: () => false };
  window.IRON_PIT_BROWSER_SUPPORT = { resolve: (sequence) => ({ events: [], sequence }), secondWind: () => null, adrenaline: () => null };
  window.IRON_PIT_BROWSER_RAGE = { enter: () => null, extendFromAttack: () => {}, endIfIncapacitated: () => {}, finalize: (sequence) => ({ event: null, sequence }) };
  window.IRON_PIT_BROWSER_ACTION_SURGE = { resolveAttack: () => null };
  window.IRON_PIT_BROWSER_SPELL_OFFENSE = { resolve: (sequence) => ({ events: [], sequence }) };
  window.IRON_PIT_BROWSER_CHARGE = { resolveClosing: (sequence) => ({ events: [], sequence, handled: false }), openingFeature: () => null };
  window.IRON_PIT_BROWSER_SAVES = { resolveTurnAction: (sequence) => ({ events: [], sequence, used: false }) };
  const target = { combatant_id: "monster-1", side: "monsters", state: { current_hp: 10, is_alive: true, is_dead: false } };
  const attack = { id: "shortbow", name: "Shortbow" };
  window.IRON_PIT_BROWSER_FORMATION = {
    targetOrder: () => [target], chooseResourceBackedAttack: () => null,
    chooseStandardAttack: () => ({ target, attack, distance: 30 }),
  };
  window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION = {
    resolve: (sequence, round, member, _target, _attack, _distance, _setup, _turnKey, extra) => {
      capturedAdvantage = extra.advantage;
      window.IRON_PIT_ACTION_ECONOMY.spend(member.state, "action");
      return { events: [{ sequence, round_number: round, event_type: "attack" }], sequence: sequence + 1 };
    },
  };
  const hero = { combatant_id: "hero-1", side: "heroes", state: {
    template: { name: "Mara", steady_aim: true, max_hp: 24 }, current_hp: 24,
    is_alive: true, is_dead: false, action_available: true, bonus_action_available: true, reaction_available: true,
  } };
  const result = window.IRON_PIT_BROWSER_TURN.resolveTurn(1, 1, hero, { heroes: [hero], monsters: [target] });
  assert.equal(capturedAdvantage, 1);
  assert.equal(hero.state.bonus_action_available, false);
  assert.equal(result.events.filter((event) => event.feature_id === "steady-aim").length, 1);
}

// Combat Prowess: one miss becomes a hit per turn, then the same turn cannot use it again.
{
  window.IRON_PIT_BROWSER_STATE = { canProne: () => false, sizeAtMost: () => false, distance: () => 5 };
  window.IRON_PIT_BROWSER_ROLLS = {
    attackMode: () => "normal",
    d20: () => ({ notation: "1d20", rolls: [5], selected_roll: 5, modifier: 0, mode: "normal", total: 5 }),
    weaponDamage: () => ({ roll: { notation: "1d6", rolls: [4], modifier: 0, selected_roll: null, mode: "normal", total: 4 }, components: [{ source: "Sword", notation: "1d6", rolls: [4], modifier: 0, damage_type: "slashing", total: 4 }] }),
  };
  window.IRON_PIT_BROWSER_ZERO_HP = { applyDamage: (state, amount) => { state.current_hp -= amount; return "damaged"; } };
  window.IRON_PIT_BROWSER_MODIFIERS = {
    attacksAgainstAdvantage: () => 0, nextAttackAgainstAdvantage: () => 0,
    consumeNextAttackAgainstAdvantage: () => 0, consumeAttacksAgainstAdvantage: () => 0,
    effectiveArmorClass: (state) => state.template.armor_class, effectiveSpeed: (state) => state.template.speed_ft || 30,
    applyD20Bonus: (_state, _kind, roll) => roll, applyHitEffects: () => {},
  };
  window.IRON_PIT_BROWSER_CONDITION_RULES = { has: () => false, attackAdvantage: () => false, autoCritical: () => false, incapacitated: () => false };
  window.IRON_PIT_ACTION_ECONOMY = { available: () => true, spend: () => {} };
  window.IRON_PIT_BROWSER_GRAPPLE = { attackDisadvantage: () => 0, speedIsZero: () => false };
  window.IRON_PIT_BROWSER_SAP = { disadvantage: () => 0, consume: () => 0, applyWeapon: () => false };
  window.IRON_PIT_BROWSER_TACTICAL_MASTER = { apply: () => false };
  load("browser-attack.js");
  const attacker = { combatant_id: "hero-1", side: "heroes", state: {
    template: { name: "Karnok", combat_prowess: true, critical_hit_minimum: 20, traits: [] },
    active_effect_ids: [], feature_last_turn_keys: {}, temporary_damage_resistances: [], current_hp: 10,
  } };
  const target = { combatant_id: "monster-1", side: "monsters", state: {
    template: { name: "Target", armor_class: 20, max_hp: 20, damage_immunities: [], damage_resistances: [], damage_vulnerabilities: [] },
    active_effect_ids: [], feature_last_turn_keys: {}, temporary_damage_resistances: [], current_hp: 20, temporary_hp: 0,
    is_alive: true, is_dead: false, is_unconscious: false, death_save_successes: 0, death_save_failures: 0,
  } };
  const attack = { id: "sword", name: "Sword", kind: "melee", bonus: 0, damageType: "slashing", diceCount: 1, diceSize: 6, damageBonus: 0, reach: 5, onHitDamage: [] };
  const first = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(1, 1, attacker, target, attack, 5, { spendAction: false, turnKey: "1:hero-1" });
  const second = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(2, 1, attacker, target, attack, 5, { spendAction: false, turnKey: "1:hero-1" });
  assert.equal(first.hit, true);
  assert.equal(first.feature_id, "boon-combat-prowess");
  assert.match(first.description, /Combat Prowess/);
  assert.equal(second.hit, false);
}

console.log("Browser advanced progression regressions passed.");
