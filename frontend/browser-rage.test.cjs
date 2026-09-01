"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters.js", "browser-monsters-fixed.js",
  "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-grapple.js", "browser-timed-conditions.js", "browser-barbarian2.js", "browser-state.js", "browser-rage.js", "browser-rolls.js",
  "browser-zero-hp.js", "browser-attack.js", "browser-healing.js", "browser-reactions.js", "browser-reaction-movement.js", "browser-saves.js",
  "browser-condition-lifecycle.js", "browser-charge.js", "browser-multiattack.js",
  "browser-spellcasting.js", "browser-condition-removal.js", "browser-support.js", "browser-turn.js",
  "browser-formation.js", "browser-engine.js",
]) load(file);

function queuedDice(values, fallback = 10) {
  const queue = [...values];
  const roll = (sides) => ((queue.length ? queue.shift() : fallback) - 1) % sides + 1;
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
}

{
  window.IRON_PIT_DICE = queuedDice([20, 1, 15, 6, 6]);
  const battle = window.IRON_PIT_BROWSER_ENGINE.runEncounter({
    hero_ids: ["rokhan-stonefury-l1"], monster_ids: ["srd-commoner"],
  });
  const rage = battle.events.find((event) => event.feature_id === "rage");
  const attack = battle.events.find((event) => event.event_type === "attack" && event.actor_id.startsWith("hero-1:"));
  assert.ok(rage, "expected Rokhan to activate Rage before attacking");
  assert.ok(attack?.hit, "expected deterministic Rokhan hit");
  assert.equal(attack.weapon_id, "rokhan-greataxe");
  assert.equal(attack.damage_roll.modifier, 5, "expected +3 Strength and +2 Rage damage");
  assert.equal(attack.damage_roll.notation, "1d12+5");
}

{
  const barbarian = structuredClone(window.IRON_PIT_BROWSER_HEROES["rokhan-stonefury-l1"]);
  const bandit = structuredClone(window.IRON_PIT_BROWSER_MONSTERS["srd-bandit"]);
  const hero = { combatant_id: "hero-1:rokhan", side: "heroes", position_ft: 0, state: window.IRON_PIT_BROWSER_STATE.buildState(barbarian) };
  const monster = { combatant_id: "monster-1:bandit", side: "monsters", position_ft: 5, state: window.IRON_PIT_BROWSER_STATE.buildState(bandit) };
  window.IRON_PIT_BROWSER_STATE.beginTurn(hero.state);
  const rage = window.IRON_PIT_BROWSER_RAGE.enter(1, 1, hero);
  assert.ok(rage);
  window.IRON_PIT_DICE = queuedDice([15, 5]);
  const scimitar = bandit.attacks.find((item) => item.id === "bandit-scimitar");
  const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(2, 1, monster, hero, scimitar, 5);
  assert.equal(event.damage_components[0].total, 6);
  assert.equal(event.damage_components[0].applied_total, 3, "Rage should halve slashing damage");
  assert.equal(hero.state.current_hp, 11);
  hero.state.is_unconscious = true;
  window.IRON_PIT_BROWSER_RAGE.endIfIncapacitated(hero.state);
  assert.equal(window.IRON_PIT_BROWSER_RAGE.active(hero.state), false, "incapacitation should end Rage");
}

{
  const barbarian = structuredClone(window.IRON_PIT_BROWSER_HEROES["rokhan-stonefury-l1"]);
  const bandit = structuredClone(window.IRON_PIT_BROWSER_MONSTERS["srd-bandit"]);
  const hero = { combatant_id: "hero-stunned-rage", side: "heroes", position_ft: 0, state: window.IRON_PIT_BROWSER_STATE.buildState(barbarian) };
  const monster = { combatant_id: "monster-stunner", side: "monsters", position_ft: 5, state: window.IRON_PIT_BROWSER_STATE.buildState(bandit) };
  window.IRON_PIT_BROWSER_STATE.beginTurn(hero.state);
  assert.ok(window.IRON_PIT_BROWSER_RAGE.enter(1, 1, hero));
  const attack = structuredClone(bandit.attacks.find((item) => item.id === "bandit-scimitar"));
  attack.controlEffect = { conditionId: "stunned", expiresAtStartOfSourceTurn: true };
  window.IRON_PIT_DICE = queuedDice([15, 1]);

  const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(2, 1, monster, hero, attack, 5);

  assert.ok(event.hit);
  assert.ok(hero.state.active_effect_ids.includes("stunned"));
  assert.equal(window.IRON_PIT_BROWSER_RAGE.active(hero.state), false, "hit-applied Incapacitation must end Rage immediately");
  assert.equal(hero.state.resources.rage, 1, "ending Rage must not refund the spent use");
}

{
  const template = structuredClone(window.IRON_PIT_BROWSER_HEROES["rokhan-stonefury-l1"]);
  const hero = { combatant_id: "hero-rage-ledger", side: "heroes", position_ft: 0, state: window.IRON_PIT_BROWSER_STATE.buildState(template) };
  const RAGE = window.IRON_PIT_BROWSER_RAGE;
  const ATTACK = window.IRON_PIT_BROWSER_ATTACK;
  const HEALING = window.IRON_PIT_BROWSER_HEALING;
  hero.state.resources["relentless-endurance"] = 0;

  assert.equal(hero.state.resources.rage, 2, "level-1 Barbarian must enter the fight with two Rage uses");
  for (const [round, remaining] of [[1, 1], [2, 0]]) {
    window.IRON_PIT_BROWSER_STATE.beginTurn(hero.state);
    assert.ok(RAGE.enter(round, round, hero), `Rage ${round} should be available`);
    assert.equal(hero.state.resources.rage, remaining);

    assert.equal(ATTACK.applyDamage(hero.state, hero.state.current_hp, false), "unconscious");
    RAGE.endIfIncapacitated(hero.state);
    assert.equal(RAGE.active(hero.state), false, "dropping to 0 HP must end active Rage");
    assert.equal(hero.state.resources.rage, remaining, "ending Rage must not refund a spent use");

    assert.equal(HEALING.restore(hero.state, 5), 5);
    assert.equal(hero.state.current_hp, 5);
    assert.equal(hero.state.is_unconscious, false);
    assert.equal(hero.state.resources.rage, remaining, "healing must not refresh encounter resources");
  }

  window.IRON_PIT_BROWSER_STATE.beginTurn(hero.state);
  assert.equal(RAGE.enter(3, 3, hero), null, "third Rage must fail after both uses were spent");
  assert.equal(hero.state.resources.rage, 0);
  assert.equal(RAGE.active(hero.state), false);
}

{
  const template = structuredClone(window.IRON_PIT_BROWSER_HEROES["rokhan-stonefury-l2"]);
  assert.ok(template, "Barbarian 2 must be generated as a browser-ready hero");
  assert.equal(template.danger_sense, true);
  assert.equal(template.reckless_attack, true);
  assert.equal(template.attacks[0].attackAbility, "strength");

  const bandit = structuredClone(window.IRON_PIT_BROWSER_MONSTERS["srd-bandit"]);
  const hero = { combatant_id: "hero-1:rokhan-stonefury-l2", side: "heroes", position_ft: 5, state: window.IRON_PIT_BROWSER_STATE.buildState(template) };
  const monster = { combatant_id: "monster-1:bandit", side: "monsters", position_ft: 10, state: window.IRON_PIT_BROWSER_STATE.buildState(bandit) };
  monster.state.template.armor_class = 99;
  window.IRON_PIT_BROWSER_STATE.beginTurn(hero.state);
  window.IRON_PIT_DICE = queuedDice([2, 15]);
  const reckless = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(1, 1, hero, monster, template.attacks[0], 5, {
    setup: { heroes: [hero], monsters: [monster] }, allowReckless: true,
  });
  assert.equal(reckless.attack_roll.mode, "advantage");
  assert.deepEqual(reckless.attack_roll.rolls, [2, 15]);
  assert.equal(reckless.feature_id, "reckless-attack");
  assert.match(reckless.description, /uses Reckless Attack/);
  assert.equal(window.IRON_PIT_BROWSER_BARBARIAN2.active(hero.state), true);

  hero.state.template.armor_class = 99;
  window.IRON_PIT_DICE = queuedDice([3, 14]);
  const scimitar = bandit.attacks.find((item) => item.id === "bandit-scimitar");
  const counter = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(2, 1, monster, hero, scimitar, 5);
  assert.equal(counter.attack_roll.mode, "advantage", "attacks against a reckless Barbarian must have Advantage");
  assert.deepEqual(counter.attack_roll.rolls, [3, 14]);

  const setup = { heroes: [hero], monsters: [monster] };
  const expired = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveSourceTiming(3, 2, hero, setup, "source_turn_start");
  assert.equal(window.IRON_PIT_BROWSER_BARBARIAN2.active(hero.state), false, "Reckless exposure ends at the next turn start");
  assert.ok(expired.events.some((event) => event.feature_id === "reckless-attack"));
}

{
  const template = structuredClone(window.IRON_PIT_BROWSER_HEROES["rokhan-stonefury-l2"]);
  const bandit = structuredClone(window.IRON_PIT_BROWSER_MONSTERS["srd-bandit"]);
  const hero = { combatant_id: "hero-oa:rokhan", side: "heroes", position_ft: 5, state: window.IRON_PIT_BROWSER_STATE.buildState(template) };
  const monster = { combatant_id: "monster-oa:bandit", side: "monsters", position_ft: 10, state: window.IRON_PIT_BROWSER_STATE.buildState(bandit) };
  monster.state.template.armor_class = 99;
  window.IRON_PIT_DICE = queuedDice([10]);
  const reactionStyle = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(1, 1, hero, monster, template.attacks[0], 5, { spendAction: false });
  assert.equal(reactionStyle.attack_roll.mode, "normal", "reaction-style attacks cannot start Reckless Attack");
  assert.deepEqual(reactionStyle.attack_roll.rolls, [10]);
  assert.equal(window.IRON_PIT_BROWSER_BARBARIAN2.active(hero.state), false);
}

{
  const template = structuredClone(window.IRON_PIT_BROWSER_HEROES["rokhan-stonefury-l2"]);
  const state = window.IRON_PIT_BROWSER_STATE.buildState(template);
  window.IRON_PIT_DICE = queuedDice([2, 15]);
  const save = window.IRON_PIT_BROWSER_SAVES.resolveSavingThrow(state, "dexterity", 12);
  assert.equal(save.roll.mode, "advantage");
  assert.deepEqual(save.roll.rolls, [2, 15]);
  assert.equal(save.roll.selected_roll, 15);

  state.active_effect_ids.push("restrained");
  window.IRON_PIT_DICE = queuedDice([10]);
  const cancelled = window.IRON_PIT_BROWSER_SAVES.resolveSavingThrow(state, "dexterity", 12);
  assert.equal(cancelled.roll.mode, "normal", "Danger Sense Advantage and Restrained Disadvantage cancel");
  assert.deepEqual(cancelled.roll.rolls, [10]);
}

console.log("Browser Rage and Barbarian 2 regressions passed.");
