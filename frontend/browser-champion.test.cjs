"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
const setDice = (values) => {
  const queue = [...values];
  window.IRON_PIT_DICE = {
    roll: () => queue.shift(),
    rollMany: (count) => Array.from({ length: count }, () => queue.shift()),
  };
};

window.IRON_PIT_BROWSER_STATE = {
  distance: (a, b) => Math.abs(a.position_ft - b.position_ft),
  nearestTarget: (member, setup) => (member.side === "heroes" ? setup.monsters : setup.heroes)
    .find((target) => target.state.is_alive && !target.state.is_dead && target.state.current_hp > 0),
  canProne: () => false, sizeAtMost: () => false,
};
load("browser-rolls.js");
load("browser-grapple.js");
load("browser-champion.js");
load("browser-attack.js");

const greatsword = { id: "greatsword", name: "Greatsword", kind: "melee", bonus: 5,
  diceCount: 2, diceSize: 6, damageBonus: 3, damageType: "slashing", reach: 5, animation: "slash" };
const shortbow = { id: "shortbow", name: "Shortbow", kind: "ranged", bonus: 3,
  diceCount: 1, diceSize: 6, damageBonus: 1, damageType: "piercing", normal: 80, long: 320, animation: "projectile" };

function state(name, kind, hp = 100) {
  return {
    template: { name, kind, armor_class: 10, max_hp: hp, speed_ft: 30, size: "medium",
      attacks: kind === "character" ? [greatsword, shortbow] : [], primary_attack_id: "greatsword",
      skill_bonuses: { athletics: 5, acrobatics: 1 }, traits: [], damage_immunities: [], damage_resistances: [],
      damage_vulnerabilities: [], critical_hit_minimum: kind === "character" ? 19 : 20,
      critical_move_fraction: kind === "character" ? 0.5 : 0, athletics_advantage: kind === "character" },
    current_hp: hp, temporary_hp: 0, is_alive: true, is_dead: false, is_unconscious: false, is_stable: false,
    death_save_successes: 0, death_save_failures: 0, action_available: true, bonus_action_available: true,
    reaction_available: true, movement_remaining_ft: 30, active_effect_ids: [], grapple_sources: [],
    timed_effects: [], temporary_damage_resistances: [], resources: { "second-wind": 2 }, feature_last_turn_keys: {},
  };
}

{
  const hero = { combatant_id: "hero-1", side: "heroes", position_ft: 0, state: state("Karnok Stoneward", "character") };
  const monster = { combatant_id: "monster-1", side: "monsters", position_ft: 20, state: state("Target", "monster") };
  const setup = { heroes: [hero], monsters: [monster] };
  setDice([19, 2, 3]);
  const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(1, 1, hero, monster, shortbow, 20, { setup });
  assert.equal(event.hit, true); assert.equal(event.critical, true); assert.equal(event.attack_roll.selected_roll, 19);
  assert.equal(event.movement_ft, 15); assert.equal(hero.position_ft, 15);
  assert.equal(monster.state.reaction_available, true, "Remarkable Athlete movement provokes no OA");
}
{
  const hero = { combatant_id: "hero-1", side: "heroes", position_ft: 5, state: state("Karnok Stoneward", "character") };
  const monster = { combatant_id: "monster-1", side: "monsters", position_ft: 10, state: state("Target", "monster") };
  setDice([19, 1, 1, 1, 1]);
  const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(1, 1, hero, monster, greatsword, 5, { setup: { heroes: [hero], monsters: [monster] } });
  assert.equal(event.critical, true); assert.equal(event.movement_ft, undefined); assert.equal(hero.position_ft, 5, "Champion never kites");
}
{
  const hero = { combatant_id: "hero-1", side: "heroes", position_ft: 5, state: state("Karnok Stoneward", "character") };
  hero.state.template.armor_class = 17; hero.state.grapple_sources = [];
  window.IRON_PIT_BROWSER_GRAPPLE.apply(hero.state, "monster-1", 15, 5, true);
  setDice([2, 15]);
  const event = window.IRON_PIT_BROWSER_GRAPPLE.escape(1, 1, hero);
  assert.equal(event.check_succeeded, true); assert.equal(event.ability_check_roll.selected_roll, 15);
}
{
  const hero = { combatant_id: "hero-1", side: "heroes", position_ft: 5, state: state("Karnok Stoneward", "character") };
  const monster = { combatant_id: "monster-1", side: "monsters", position_ft: 10, state: state("AC 30", "monster") };
  monster.state.template.armor_class = 30; setDice([19]);
  const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(1, 1, hero, monster, greatsword, 5);
  assert.equal(event.hit, false); assert.equal(event.critical, false, "natural 19 is not an automatic hit");
}

// Prove engine initiative uses Champion Advantage without requiring a full combat turn.
window.IRON_PIT_BROWSER_HEROES = { champion: { name: "Karnok", kind: "character", level: 3, speed_ft: 30,
  initiative_bonus: 1, initiative_advantage: true, attacks: [greatsword], primary_attack_id: "greatsword" } };
window.IRON_PIT_BROWSER_MONSTERS = { target: { name: "Target", kind: "monster", challenge_rating: "0", speed_ft: 30,
  initiative_bonus: 0, attacks: [], primary_attack_id: null } };
window.IRON_PIT_BROWSER_FORMATION = { startingPosition: (_template, side) => side === "heroes" ? 5 : 10 };
window.IRON_PIT_BROWSER_PRECOMBAT_SPELLS = { prepare: (_setup, sequence) => ({ events: [], sequence }) };
window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE = {
  resolveTargetTiming: (sequence) => ({ events: [], sequence }), resolveSourceTiming: (sequence) => ({ events: [], sequence }),
};
window.IRON_PIT_BROWSER_TURN = { resolveTurn: (sequence, _round, _member, setup) => {
  setup.monsters[0].state.is_dead = true; setup.monsters[0].state.is_alive = false; setup.monsters[0].state.current_hp = 0;
  return { events: [], sequence };
} };
window.IRON_PIT_BROWSER_STATE.buildState = (template) => ({ template, current_hp: 10, is_alive: true, is_dead: false,
  is_unconscious: false, is_stable: false, active_effect_ids: [], reaction_available: true });
window.IRON_PIT_BROWSER_STATE.refreshReaction = (s) => { s.reaction_available = true; };
global.crypto = { randomUUID: () => "battle-test" };
setDice([4, 17, 10]);
load("browser-engine.js");
{
  const battle = window.IRON_PIT_BROWSER_ENGINE.runEncounter({ hero_ids: ["champion"], monster_ids: ["target"] });
  const heroGroup = battle.initiative.groups.find((group) => group.side === "heroes");
  assert.equal(heroGroup.natural_roll, 17); assert.equal(heroGroup.initiative_count, 18);
}

for (const htmlName of ["index.html", path.join("..", "index.html")]) {
  const html = fs.readFileSync(path.join(__dirname, htmlName), "utf8");
  assert.match(html, /browser-champion\.js/);
}

console.log("Browser Champion Fighter 3 regressions passed.");
