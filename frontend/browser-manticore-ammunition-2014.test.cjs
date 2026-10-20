"use strict";
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

const S = window.IRON_PIT_BROWSER_STATE;
const M = window.IRON_PIT_BROWSER_MULTIATTACK;
const C = window.IRON_PIT_BROWSER_MULTIATTACK_CHOICES;
const F = window.IRON_PIT_BROWSER_FORMATION;
const card = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-manticore"];
assert.ok(card, "The actual generated Manticore card must be runnable.");
const cardBefore = structuredClone(card);
const actor = { combatant_id: "manticore", side: "monsters", state: S.buildState(card) };
const target = { combatant_id: "target", side: "heroes",
  state: S.buildState(window.IRON_PIT_BROWSER_MONSTERS_2014["2014-commoner"]) };
actor.state.position = { x: 6, y: 6 };
target.state.position = { x: 2, y: 6 };
const setup = { heroes: [target], monsters: [actor], ruleset: "2014" };
const roll = sides => sides === 20 ? 2 : 1;
window.IRON_PIT_DICE = { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };

// Resolve every printed shot using the real exported source, not a replacement card.
const shots = [];
for (let round = 1; round <= 8; round += 1) {
  S.beginTurn(actor.state);
  assert.equal(C.selectSequence(actor, setup)?.variant.attackKind, "ranged");
  const events = M.resolveAttackAction(1, round, actor, setup).events.filter(e => e.event_type === "attack");
  assert.equal(events.length, 3);
  assert.ok(events.every(e => e.attack_name === "Tail Spike" && !e.hit));
  shots.push(...events);
}
assert.deepEqual(shots.map(e => e.resource_remaining), Array.from({ length: 24 }, (_, index) => 23 - index));
assert.equal(actor.state.resources["tail-spike"], 0);
assert.equal(C.selectSequence(actor, setup), null);
assert.equal(F.chooseStandardAttack(actor, setup), null);
const spike = card.attacks.find(attack => attack.resourceId === "tail-spike");
const depleted = structuredClone(actor.state);
assert.throws(() => window.IRON_PIT_BROWSER_ATTACK.resolveAttack(1, 9, actor, target, spike, 20,
  { spendAction: false, setup }), /insufficient ammunition/);
assert.deepEqual(actor.state, depleted, "An unavailable shot cannot change state.");

// Empty ranged resources do not disable the independently printed melee option.
target.state.position = { x: 5, y: 6 };
S.beginTurn(actor.state);
assert.equal(C.selectSequence(actor, setup)?.variant.attackKind, "melee");
const melee = M.resolveAttackAction(1, 9, actor, setup).events.filter(e => e.event_type === "attack");
assert.deepEqual(melee.map(e => e.attack_name), ["Bite", "Claw", "Claw"]);
assert.equal(actor.state.resources["tail-spike"], 0);
assert.deepEqual(card, cardBefore, "Fighting must not mutate the source card.");
assert.equal(S.buildState(card).resources["tail-spike"], 24, "Reusing the same card starts a fresh allowance.");

// Natural 1 automatically misses but every printed shot is still attempted.
actor.state = S.buildState(card);
actor.state.position = { x: 6, y: 6 };
target.state.position = { x: 2, y: 6 };
window.IRON_PIT_DICE = { roll: () => 1, rollMany: () => { throw new Error("A miss cannot roll damage."); } };
const interrupted = M.resolveAttackAction(1, 1, actor, setup).events.filter(e => e.event_type === "attack");
assert.equal(interrupted.length, 3);
assert.deepEqual(interrupted.map(e => e.resource_remaining), [23, 22, 21]);
assert.ok(interrupted.every(e => e.hit === false && e.turn_terminated === false));
assert.equal(actor.state.turn_terminated, false);
S.beginTurn(actor.state);
assert.equal(actor.state.resources["tail-spike"], 21, "A new turn is not a new fight or a long rest.");

// The separately sourced 2024 card does not inherit 2014's printed regrowth limit.
const card2024 = window.IRON_PIT_BROWSER_MONSTERS["srd-manticore"];
assert.ok(card2024);
assert.equal(card2024.attacks.find(attack => attack.name === "Tail Spike").resourceId, undefined);
assert.deepEqual(card2024.resources, {});

// Exercise the whole production encounter loop as well as the isolated ranged window.
require("node:vm").runInThisContext(require("node:fs").readFileSync(
  require("node:path").join(__dirname, "browser-turbo.js"), "utf8"), { filename: "browser-turbo.js" });
const hero = Object.values(window.IRON_PIT_BROWSER_HEROES)
  .find(item => item.ruleset === "2014" && item.class_id === "fighter" && item.level === 5);
assert.ok(hero);
for (const count of [1, 6]) {
  const selection = { ruleset: "2014", hero_ids: Array(count).fill(hero.id),
    monster_ids: Array(count).fill(card.id) };
  const first = window.IRON_PIT_BROWSER_TURBO.runSeeded(selection, 20261018 + count).battle;
  const replay = window.IRON_PIT_BROWSER_TURBO.runSeeded(selection, 20261018 + count).battle;
  assert.deepEqual(first.events, replay.events, `${count}v${count} must replay the same event stream.`);
  assert.equal(first.outcome, replay.outcome);
  assert.equal(first.setup.monsters.length, count);
  assert.ok(first.setup.monsters.every(member => member.state.resources["tail-spike"] >= 0));
  assert.deepEqual(card, cardBefore, "Whole encounters also preserve the source card.");
}
console.log("Canonical 2014 Manticore: 24 misses, exhaustion, melee fallback, interruption, immutable reset and edition isolation passed.");
