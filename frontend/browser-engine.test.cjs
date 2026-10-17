"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;

const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters.js", "browser-monsters-fixed.js",
  "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js", "browser-ability-hooks.js", "browser-ability-checks.js",
  "browser-grapple.js", "browser-timed-conditions.js", "browser-timed-control-limits.js", "browser-weapon-mastery.js",
  "browser-state.js", "browser-resources.js", "browser-resource-conversion.js", "browser-rage.js", "browser-rolls.js", "browser-zero-hp.js",
  "browser-damage-defense-rules.js", "browser-graze.js", "browser-vex.js", "browser-attack-outcome.js", "browser-attack.js", "browser-reactions.js",
  "browser-dodge.js", "browser-saving-throws.js", "browser-failed-save-timed-effects.js", "browser-saves.js", "browser-condition-lifecycle.js", "browser-charge.js",
  "browser-light-weapons.js", "browser-light-attack.js", "browser-standard-attack-action.js",
  "browser-multiattack-choices.js", "browser-multiattack.js", "browser-spellcasting.js", "browser-spell-area.js",
  "browser-healing-policy.js", "browser-healing-resolution.js", "browser-group-healing.js", "browser-healing.js",
  "browser-condition-removal.js", "browser-support.js", "browser-formation.js", "browser-arena-map.js", "browser-grid-geometry.js",
  "browser-grid-movement-support.js", "browser-grid-path-search-support.js", "browser-grid-path-search.js",
  "browser-grid-movement.js", "browser-grid-reaction-support.js", "browser-reaction-movement.js",
  "browser-offensive-ranges.js", "browser-offensive-movement.js", "browser-grid-placement.js",
  "browser-frenzy-2014.js", "browser-2014-monk.js", "browser-steady-aim.js", "browser-persistent-spell-attacks.js", "browser-targeted-concentration-damage.js", "browser-bonus-attacks.js",
  "browser-tactical-actions.js", "browser-timed-self-buff-policy.js", "browser-timed-self-buffs.js", "browser-ability-hook-installation.js", "browser-main-action-profiles.js", "browser-main-action-selection.js", "browser-main-action-providers.js", "browser-spell-offense.js", "browser-turn.js", "browser-initiative.js", "browser-initiative-resource-refill.js", "browser-engine.js",
]) load(file);

function deterministicDice(seed = 12345) {
  let state = seed >>> 0;
  const roll = (sides) => {
    state = (1664525 * state + 1013904223) >>> 0;
    return (state % sides) + 1;
  };
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
}

function queuedDice(values, fallback = 10) {
  const queue = [...values];
  const roll = (sides) => {
    const raw = queue.length ? queue.shift() : fallback;
    return ((raw - 1) % sides) + 1;
  };
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
}

function fight(heroIds, monsterIds, dice = deterministicDice()) {
  window.IRON_PIT_DICE = dice;
  return window.IRON_PIT_BROWSER_ENGINE.runEncounter({ hero_ids: heroIds, monster_ids: monsterIds });
}

{
  const battle = fight(["karnok-stoneward-l1"], ["srd-commoner"]);
  assert.notEqual(battle.outcome, "active");
  assert.ok(battle.events.some((event) => event.event_type === "attack"));
  assert.deepEqual(
    [battle.setup.map_definition.width_squares, battle.setup.map_definition.height_squares],
    [24, 16],
  );
  assert.ok(battle.setup.heroes[0].state.position, "hero must have authoritative grid position");
  assert.ok(battle.setup.monsters[0].state.position, "monster must have authoritative grid position");
  assert.equal(Object.hasOwn(battle.setup, "starting_distance_ft"), false, "setup must not expose configurable scalar distance");
  assert.ok(window.IRON_PIT_BROWSER_STATE.distance(battle.setup.heroes[0], battle.setup.monsters[0]) >= 5);
}

{
  const batTemplate = structuredClone(window.IRON_PIT_BROWSER_MONSTERS["srd-bat"]);
  const heroTemplate = structuredClone(window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"]);
  const bat = { combatant_id: "monster-1:bat", side: "monsters", position_ft: 5, state: window.IRON_PIT_BROWSER_STATE.buildState(batTemplate) };
  const hero = { combatant_id: "hero-1:karnok", side: "heroes", position_ft: 0, state: window.IRON_PIT_BROWSER_STATE.buildState(heroTemplate) };
  window.IRON_PIT_BROWSER_STATE.beginTurn(bat.state);
  window.IRON_PIT_DICE = queuedDice([20]);
  const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(1, 1, bat, hero, batTemplate.attacks[0], 5);
  assert.equal(event.critical, true);
  assert.equal(event.damage_roll.notation, "1");
  assert.deepEqual(event.damage_roll.rolls, []);
  assert.equal(event.damage_roll.total, 1, "fixed damage must not double on a critical hit");
}

{
  const battle = fight(["karnok-stoneward-l1"], ["srd-bandit"], deterministicDice(7));
  const karnokAttacks = battle.events.filter((event) => event.event_type === "attack" && event.actor_id.startsWith("hero-1:"));
  assert.ok(karnokAttacks.length > 0, "Karnok should eventually make a legal attack after grid approach");
}

{
  const battle = fight(["karnok-stoneward-l1"], ["srd-dire-wolf", "srd-dire-wolf"], queuedDice([1, 20, 20, 20, 10, 10, 10]));
  const packAttack = battle.events.find((event) => event.event_type === "attack" && event.feature_id === "pack-tactics");
  assert.ok(packAttack, "expected Pack Tactics attack");
  assert.equal(packAttack.attack_roll.mode, "advantage");
}

{
  const battle = fight(["karnok-stoneward-l1"], ["srd-dire-wolf"],
    queuedDice([20, 1, 20, 1, 1, 1, 1, 1, 1, 1, 1, 10, 1]));
  assert.ok(battle.events.some((event) => event.event_type === "attack" && event.critical), "expected a critical attack");
  assert.ok(battle.events.some((event) => event.event_type === "attack" && event.attack_roll.selected_roll === 1), "expected a natural 1 attack");
}

{
  const battle = fight(["karnok-stoneward-l1"], ["srd-wolf", "srd-wolf"],
    queuedDice([1, 20, 20, 20, 6, 6, 10, 10]));
  assert.ok(battle.events.some((event) => event.applied_condition_ids?.includes("prone")), "expected Wolf/Dire Wolf Prone support");
}

{
  const battle = fight(["karnok-stoneward-l1"], ["srd-black-bear"], queuedDice([1, 20, 15, 1, 15, 1]));
  const strikes = battle.events.filter((event) => event.event_type === "attack" && event.actor_id.startsWith("monster-1:"));
  assert.ok(strikes.length >= 2, "Black Bear should eventually execute its two-Rend Multiattack");
  assert.deepEqual(strikes.slice(0, 2).map((event) => event.weapon_id), ["black-bear-rend", "black-bear-rend"]);
}

{
  const battle = fight(["karnok-stoneward-l1"], ["srd-brown-bear"], queuedDice([1, 20, 15, 1, 15, 1]));
  const strikes = battle.events.filter((event) => event.event_type === "attack" && event.actor_id.startsWith("monster-1:"));
  assert.ok(strikes.length >= 2, "Brown Bear should eventually execute its Multiattack");
  assert.deepEqual(strikes.slice(0, 2).map((event) => event.weapon_id), ["brown-bear-bite", "brown-bear-claw"]);
}

{
  const heroTemplate = structuredClone(window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"]);
  const boarTemplate = structuredClone(window.IRON_PIT_BROWSER_MONSTERS["srd-boar"]);
  const hero = { combatant_id: "hero-1:karnok", side: "heroes", position_ft: 0, state: window.IRON_PIT_BROWSER_STATE.buildState(heroTemplate) };
  const boar = { combatant_id: "monster-1:boar", side: "monsters", position_ft: 5, state: window.IRON_PIT_BROWSER_STATE.buildState(boarTemplate) };
  boar.state.current_hp = 6;
  window.IRON_PIT_DICE = queuedDice([4, 15, 3]);
  const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(1, 1, boar, hero, boarTemplate.attacks[0], 5);
  assert.equal(event.attack_roll.mode, "advantage");
  assert.equal(event.attack_roll.selected_roll, 15);
}

{
  const battle = fight(["rokhan-stonefury-l1"], ["srd-commoner"], queuedDice([20, 1, 15, 6, 6]));
  const rage = battle.events.find((event) => event.actor_id.startsWith("hero-1:") && event.feature_id === "rage");
  const attack = battle.events.find((event) => event.actor_id.startsWith("hero-1:") && event.event_type === "attack");
  assert.ok(rage, "audited Barbarian should Rage in combat");
  assert.ok(battle.events.some((event) => event.actor_id.startsWith("hero-1:") && event.event_type === "movement"), "Rokhan should close with legal movement under no-kiting AI");
  assert.equal(attack?.weapon_id, "rokhan-greataxe", "Rokhan should use melee after closing to legal reach from the compact starting formation");
}

{
  const heroes = Array(6).fill("karnok-stoneward-l1");
  const monsters = Array(6).fill("srd-wolf");
  const battle = fight(heroes, monsters, deterministicDice(42));
  assert.notEqual(battle.outcome, "active");
  assert.ok(battle.rounds <= 100);
  assert.equal(battle.setup.heroes.length, 6);
  assert.equal(battle.setup.monsters.length, 6);
  assert.throws(() => fight(Array(7).fill("karnok-stoneward-l1"), ["srd-wolf"]), /1-6 cards per side/);
}

{
  const id = "initiative-refill-engine-fixture";
  const template = structuredClone(window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"]);
  template.id = id;
  template.name = "Initiative Refill Fixture";
  template.resources = { ...(template.resources || {}), focus: 5 };
  template.initiative_resource_refill_grants = [{
    source_id: "second-breath", source_name: "Second Breath",
    resource_id: "focus", when_at_or_below: 0, restore_amount: 4,
  }];
  window.IRON_PIT_BROWSER_HEROES[id] = template;

  const originalBuildState = window.IRON_PIT_BROWSER_STATE.buildState;
  window.IRON_PIT_BROWSER_STATE.buildState = (candidate) => {
    const state = originalBuildState(candidate);
    if (candidate.id === id) state.resources.focus = 0;
    return state;
  };
  try {
    const battle = fight([id], ["srd-commoner"], deterministicDice(2020));
    const refillIndex = battle.events.findIndex((event) => event.feature_id === "second-breath");
    const firstTurnIndex = battle.events.findIndex((event) => event.round_number >= 1 && event.actor_id !== "arena");
    assert.ok(refillIndex >= 0, "live browser engine must execute initiative resource refill");
    assert.ok(firstTurnIndex > refillIndex, "initiative resource refill must resolve before combat turns");
    assert.equal(battle.events[refillIndex].resource_remaining, 4);
  } finally {
    window.IRON_PIT_BROWSER_STATE.buildState = originalBuildState;
    delete window.IRON_PIT_BROWSER_HEROES[id];
  }
}

console.log("Browser combat regressions passed.");
require("./browser-initiative-natural-one.test.cjs");

{
  const custom = structuredClone(window.IRON_PIT_BROWSER_MONSTERS["srd-goblin-warrior"]);
  custom.id = "synthetic-unlisted-monster";
  const hero = Object.values(window.IRON_PIT_BROWSER_HEROES).find(row => row.ruleset === "2024");
  const selection = {ruleset:"2024",hero_ids:[hero.id],monster_ids:[custom.id],compiled_monsters:{[custom.id]:custom}};
  const result = window.IRON_PIT_BROWSER_ENGINE.runEncounter(selection);
  assert.ok(result.events.length);
  assert.equal(Object.hasOwn(window.IRON_PIT_BROWSER_MONSTERS,custom.id),false);
}

{
  // Certified cards must be reusable across battles without fight-state leakage.
  const encounters = [
    { heroes: ["karnok-stoneward-l1"], monsters: ["srd-bandit"] },
    { heroes: ["rokhan-stonefury-l1"], monsters: ["srd-commoner"] },
    { heroes: ["karnok-stoneward-l1", "rokhan-stonefury-l1"], monsters: ["srd-wolf", "srd-wolf"] },
  ];
  for (const [index, encounter] of encounters.entries()) {
    const run = () => fight(encounter.heroes, encounter.monsters, deterministicDice(800 + index));
    const beforeHeroes = encounter.heroes.map(id => JSON.stringify(window.IRON_PIT_BROWSER_HEROES[id]));
    const beforeMonsters = encounter.monsters.map(id => JSON.stringify(window.IRON_PIT_BROWSER_MONSTERS[id]));
    const first = run(), second = run();
    assert.notEqual(first.outcome, "active", "certified pregen/monster encounter must resolve");
    assert.equal(first.outcome, second.outcome, "same seed and immutable cards must resolve identically");
    assert.equal(first.rounds, second.rounds, "repeated fight rounds must match");
    assert.deepEqual(first.events.map(event => [event.event_type, event.actor_id, event.target_id, event.damage_roll?.total]),
      second.events.map(event => [event.event_type, event.actor_id, event.target_id, event.damage_roll?.total]),
      "repeated fights must have identical observable combat events");
    assert.deepEqual(encounter.heroes.map(id => JSON.stringify(window.IRON_PIT_BROWSER_HEROES[id])), beforeHeroes,
      "a fight must not mutate certified pregen definitions");
    assert.deepEqual(encounter.monsters.map(id => JSON.stringify(window.IRON_PIT_BROWSER_MONSTERS[id])), beforeMonsters,
      "a fight must not mutate certified monster definitions");
  }
}

{
  // Beta gate: completed encounters preserve fundamental combat-state bounds.
  // Exercise the existing engine; do not calculate combat outcomes here.
  const scenarios = [
    [["karnok-stoneward-l1"], ["srd-bandit"]],
    [["rokhan-stonefury-l1"], ["srd-commoner"]],
    [["karnok-stoneward-l1", "rokhan-stonefury-l1"], ["srd-wolf", "srd-wolf"]],
  ];
  for (const [index, [heroes, monsters]] of scenarios.entries()) {
    const battle = fight(heroes, monsters, deterministicDice(19400 + index));
    assert.notEqual(battle.outcome, "active");
    for (const member of [...battle.setup.heroes, ...battle.setup.monsters]) {
      const state = member.state;
      assert.ok(Number.isFinite(state.current_hp), "HP must remain finite");
      assert.ok(Number.isFinite(state.temporary_hp) && state.temporary_hp >= 0, "temporary HP must be nonnegative");
      assert.ok(state.current_hp >= 0, "HP cannot be negative");
      assert.ok(state.current_hp <= window.IRON_PIT_BROWSER_STATE.effectiveMaxHp(state), "HP cannot exceed effective maximum");
      assert.equal(Boolean(state.is_alive && state.is_dead), false, "alive and dead states cannot coexist");
      assert.ok(Number.isInteger(state.death_save_successes) && state.death_save_successes >= 0 && state.death_save_successes <= 3);
      assert.ok(Number.isInteger(state.death_save_failures) && state.death_save_failures >= 0 && state.death_save_failures <= 3);
      assert.ok(Object.values(state.resources || {}).every(value => Number.isInteger(value) && value >= 0),
        "resource counters must be nonnegative integers");
    }
  }
}

{
  // Beta gate: full 6-vs-6 must resolve deterministically with isolated state.
  // Use actual certified cards, repeating IDs only as distinct combatant instances.
  const heroes = Array(6).fill("karnok-stoneward-l1");
  const monsters = Array(6).fill("srd-commoner");
  const run = () => fight(heroes, monsters, deterministicDice(62026));
  const beforeHero = JSON.stringify(window.IRON_PIT_BROWSER_HEROES[heroes[0]]);
  const beforeMonster = JSON.stringify(window.IRON_PIT_BROWSER_MONSTERS[monsters[0]]);
  const first = run(), second = run();
  assert.notEqual(first.outcome, "active", "6v6 must reach a terminal outcome");
  assert.equal(first.setup.heroes.length, 6, "all six heroes must be instantiated");
  assert.equal(first.setup.monsters.length, 6, "all six monsters must be instantiated");
  assert.equal(window.IRON_PIT_BATTLE_LAB?.fingerprint?.(first) || JSON.stringify(first.events),
    window.IRON_PIT_BATTLE_LAB?.fingerprint?.(second) || JSON.stringify(second.events),
    "six-versus-six seeded replay must match");
  assert.equal(JSON.stringify(window.IRON_PIT_BROWSER_HEROES[heroes[0]]), beforeHero);
  assert.equal(JSON.stringify(window.IRON_PIT_BROWSER_MONSTERS[monsters[0]]), beforeMonster);
  for (const member of [...first.setup.heroes, ...first.setup.monsters]) {
    const state = member.state;
    assert.ok(Number.isFinite(state.current_hp) && state.current_hp >= 0);
    assert.ok(state.current_hp <= window.IRON_PIT_BROWSER_STATE.effectiveMaxHp(state));
    assert.ok(!(state.is_alive && state.is_dead));
  }
}

{
  // Beta gate: mixed card definitions must coexist in a full party battle.
  // Avoid treating six copies of one card as sufficient mixed-party coverage.
  const heroes = ["karnok-stoneward-l1", "rokhan-stonefury-l1", "karnok-stoneward-l1",
    "rokhan-stonefury-l1", "karnok-stoneward-l1", "rokhan-stonefury-l1"];
  const monsters = ["srd-commoner", "srd-bandit", "srd-wolf",
    "srd-commoner", "srd-bandit", "srd-wolf"];
  const run = () => fight(heroes, monsters, deterministicDice(622026));
  const snapshots = [...new Set(heroes)].map(id => JSON.stringify(window.IRON_PIT_BROWSER_HEROES[id]))
    .concat([...new Set(monsters)].map(id => JSON.stringify(window.IRON_PIT_BROWSER_MONSTERS[id])));
  const first = run(), second = run();
  assert.notEqual(first.outcome, "active", "mixed 6v6 must terminate");
  assert.equal(first.setup.heroes.length, 6);
  assert.equal(first.setup.monsters.length, 6);
  const instances = [...first.setup.heroes, ...first.setup.monsters];
  assert.equal(new Set(instances.map(member => member.combatant_id)).size, 12,
    "repeated source cards must create twelve separate combatants");
  assert.equal(new Set(instances.map(member => member.state)).size, 12,
    "each participant must own isolated fight state");
  assert.equal(first.outcome, second.outcome);
  assert.equal(first.rounds, second.rounds);
  assert.deepEqual(first.events, second.events, "mixed 6v6 must replay the same events");
  assert.deepEqual([...new Set(heroes)].map(id => JSON.stringify(window.IRON_PIT_BROWSER_HEROES[id]))
    .concat([...new Set(monsters)].map(id => JSON.stringify(window.IRON_PIT_BROWSER_MONSTERS[id]))), snapshots,
    "mixed 6v6 must leave all distinct card definitions unchanged");
  for (const member of [...first.setup.heroes, ...first.setup.monsters]) {
    assert.ok(Number.isFinite(member.state.current_hp) && member.state.current_hp >= 0);
    assert.ok(member.state.current_hp <= window.IRON_PIT_BROWSER_STATE.effectiveMaxHp(member.state));
    assert.ok(!(member.state.is_alive && member.state.is_dead));
  }
}
