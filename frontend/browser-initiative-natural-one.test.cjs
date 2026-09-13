"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters-generated.js", "browser-condition-immunity.js", "browser-condition-rules.js",
  "browser-action-economy.js", "browser-grapple.js", "browser-timed-conditions.js", "browser-state.js", "browser-rage.js", "browser-rolls.js",
  "browser-zero-hp.js", "browser-weapon-mastery.js", "browser-graze.js", "browser-vex.js", "browser-attack.js",
  "browser-reactions.js", "browser-saves.js", "browser-charge.js", "browser-light-weapons.js", "browser-light-attack.js",
  "browser-standard-attack-action.js", "browser-multiattack.js", "browser-action-surge.js", "browser-formation.js",
  "browser-initiative.js",
]) load(file);

function queuedDice(values, fallback = 10) {
  const queue = [...values];
  const roll = (sides) => {
    const raw = queue.length ? queue.shift() : fallback;
    return ((raw - 1) % sides) + 1;
  };
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
}

assert.equal(window.IRON_PIT_CANONICAL_MONSTERS_READY, true, "initiative regressions must use the canonical generated monster roster");

function member(template, side, id, position) {
  return { combatant_id: id, side, position_ft: position, state: window.IRON_PIT_BROWSER_STATE.buildState(structuredClone(template)) };
}

function basicSetup(monsterId = "srd-commoner", heroId = "karnok-stoneward-l1") {
  const hero = member(window.IRON_PIT_BROWSER_HEROES[heroId], "heroes", `hero-1:${heroId}`, 5);
  const monster = member(window.IRON_PIT_BROWSER_MONSTERS[monsterId], "monsters", `monster-1:${monsterId}`, 10);
  assert.ok(monster.state.template, `${monsterId} must exist in the generated certified roster`);
  return { heroes: [hero], monsters: [monster], hero, monster };
}

function neutralizeInitiative(setup) {
  for (const combatant of [...setup.heroes, ...setup.monsters]) {
    combatant.state.template.initiative_bonus = 0;
    combatant.state.template.initiative_advantage = false;
  }
}

{
  const setup = basicSetup(); neutralizeInitiative(setup);
  window.IRON_PIT_DICE = queuedDice([20, 19]);
  const initiative = window.IRON_PIT_BROWSER_INITIATIVE.resolve(setup);
  assert.equal(initiative.groups[0].side, "heroes");
  assert.equal(initiative.groups[0].natural_roll, 20);
}

{
  const setup = basicSetup(); neutralizeInitiative(setup);
  window.IRON_PIT_DICE = queuedDice([1, 2]);
  const initiative = window.IRON_PIT_BROWSER_INITIATIVE.resolve(setup);
  assert.equal(initiative.groups.at(-1).side, "heroes");
  assert.equal(initiative.groups.at(-1).natural_roll, 1);
}

{
  const setup = basicSetup(); neutralizeInitiative(setup);
  window.IRON_PIT_DICE = queuedDice([10, 10, 5, 5, 7, 12]);
  const initiative = window.IRON_PIT_BROWSER_INITIATIVE.resolve(setup);
  const hero = initiative.groups.find((group) => group.side === "heroes");
  const monster = initiative.groups.find((group) => group.side === "monsters");
  assert.deepEqual(hero.tie_break_rolls, [5, 7]);
  assert.deepEqual(monster.tie_break_rolls, [5, 12]);
  assert.equal(initiative.groups[0].side, "monsters");
}

{
  const { hero, monster } = basicSetup();
  window.IRON_PIT_BROWSER_STATE.beginTurn(monster.state);
  window.IRON_PIT_DICE = queuedDice([1]);
  const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(
    1, 1, monster, hero, monster.state.template.attacks[0], 5,
  );
  assert.equal(event.hit, false);
  assert.equal(event.attack_roll.selected_roll, 1);
  assert.equal(event.turn_terminated, true);
  assert.equal(event.turn_termination_reason, "iron-pit-natural-1-attack");
  assert.equal(monster.state.turn_terminated, true);
  assert.equal(monster.state.action_available, false);
  assert.equal(monster.state.bonus_action_available, false);
  assert.equal(monster.state.movement_remaining_ft, 0);
  assert.equal(monster.state.reaction_available, true);
  assert.match(event.description, /immediately ends the attacker's turn/);

  window.IRON_PIT_BROWSER_STATE.beginTurn(monster.state);
  assert.equal(monster.state.turn_terminated, false);
  assert.equal(monster.state.action_available, true);
  assert.equal(monster.state.bonus_action_available, true);
  assert.equal(monster.state.reaction_available, true);
}

{
  const { hero: mover, monster: reactor } = basicSetup();
  const setup = { heroes: [mover], monsters: [reactor] };
  window.IRON_PIT_BROWSER_STATE.beginTurn(reactor.state);
  window.IRON_PIT_DICE = queuedDice([1]);
  const event = window.IRON_PIT_BROWSER_REACTIONS.resolveOpportunityAttack(
    1, 1, reactor, mover, setup, 5, 10, "speed",
  );
  assert.ok(event);
  assert.equal(event.attack_roll.selected_roll, 1);
  assert.equal(event.hit, false);
  assert.equal(event.turn_terminated, false);
  assert.equal(event.turn_termination_reason, null);
  assert.equal(reactor.state.turn_terminated, false);
  assert.equal(reactor.state.action_available, true);
  assert.equal(reactor.state.bonus_action_available, true);
  assert.equal(reactor.state.reaction_available, false);
  assert.match(event.description, /does not terminate a future turn/);
}

{
  const { hero, monster: bear } = basicSetup("srd-black-bear");
  const setup = { heroes: [hero], monsters: [bear] };
  window.IRON_PIT_BROWSER_STATE.beginTurn(bear.state);
  window.IRON_PIT_DICE = queuedDice([1]);
  const result = window.IRON_PIT_BROWSER_MULTIATTACK.resolveAttackAction(1, 1, bear, setup);
  const attacks = result.events.filter((event) => event.event_type === "attack");
  assert.equal(attacks.length, 1);
  assert.equal(attacks[0].attack_roll.selected_roll, 1);
  assert.equal(bear.state.turn_terminated, true);
}

{
  const { hero: fighter } = basicSetup("srd-commoner", "karnok-stoneward-l2");
  fighter.state.turn_terminated = true;
  fighter.state.turn_termination_reason = "iron-pit-natural-1-attack";
  fighter.state.action_available = false;
  fighter.state.resources["action-surge"] = 1;
  assert.equal(window.IRON_PIT_BROWSER_ACTION_SURGE.available(fighter.state, "1:hero-1:karnok-stoneward-l2"), false);
}

console.log("Canonical generated Iron Pit initiative/natural-1 browser regressions passed.");
