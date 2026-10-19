"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { loadWebsite } = require("./browser-test-runtime.cjs");
loadWebsite();
const cases = JSON.parse(fs.readFileSync(path.join(__dirname, "test-fixtures/multiattack-sequences.json"), "utf8"));
const fixture = cases.find(item => item.id === "bandit-captain-20");
assert.ok(fixture, "Source Multiattack fixture is required.");
const S = window.IRON_PIT_BROWSER_STATE;
const MC = window.IRON_PIT_BROWSER_MULTIATTACK_CHOICES;
const F = window.IRON_PIT_BROWSER_FORMATION;
function setupFor(ammo) {
  const card = structuredClone(fixture.actor);
  const melee = card.attacks.find(attack => attack.kind === "melee");
  const ranged = card.attacks.find(attack => attack.kind === "ranged");
  assert.ok(melee && ranged);
  card.attacks = [
    { ...melee, id: "bite", name: "Bite" },
    { ...melee, id: "claw", name: "Claw" },
    { ...ranged, id: "spike", name: "Tail Spike", resourceId: "spikes", resourceCost: 1 },
  ];
  card.resources = { spikes: ammo };
  card.attack_action = { id: "grouped", name: "Multiattack", isAttackAction: false, variants: [
    { id: "melee", attackKind: "melee", slots: [
      { attackIds: ["bite"] }, { attackIds: ["claw"] }, { attackIds: ["claw"] },
    ] },
    { id: "ranged", attackKind: "ranged", slots: [
      { attackIds: ["spike"] }, { attackIds: ["spike"] }, { attackIds: ["spike"] },
    ] },
  ] };
  const actor = { combatant_id: "actor", side: "monsters", state: S.buildState(card) };
  const target = { combatant_id: "target", side: "heroes", state: S.buildState(structuredClone(fixture.target)) };
  actor.state.position = { x: 6, y: 6 }; actor.state.formation_row = "back";
  target.state.position = { x: 2, y: 6 };
  const setup = { heroes: [target], monsters: [actor], ruleset: "2014" };
  return { actor, target, setup };
}
{
  const { actor, setup } = setupFor(24);
  const prior = structuredClone(actor.state);
  assert.equal(MC.selectSequence(actor, setup)?.variant.id, "ranged");
  assert.deepEqual(actor.state, prior, "Source sequence preview cannot consume ammunition");
  window.IRON_PIT_DICE = { roll: sides => sides === 20 ? 2 : 1, rollMany: (n, sides) => Array(n).fill(sides === 20 ? 2 : 1) };
  const events = window.IRON_PIT_BROWSER_MULTIATTACK.resolveAttackAction(1, 1, actor, setup)
    .events.filter(event => event.event_type === "attack");
  assert.equal(events.length, 3);
  assert.deepEqual(events.map(event => event.resource_remaining), [23, 22, 21]);
  assert.ok(events.every(event => !event.hit && event.description.includes("ammunition remaining")));
  assert.equal(actor.state.resources.spikes, 21);
}
{
  const { actor, setup } = setupFor(2);
  assert.equal(MC.selectSequence(actor, setup), null, "Three-shot option needs three ammunition");
  assert.equal(F.chooseStandardAttack(actor, setup).attack.id, "spike");
  actor.state.resources.spikes = 0;
  assert.equal(F.chooseStandardAttack(actor, setup), null);
  assert.equal(MC.selectSequence(actor, setup), null);
  assert.equal(setupFor(24).actor.state.resources.spikes, 24, "New fight restores source ammunition");
}
console.log("Universal browser ammunition: preview, three misses, depletion, fallback and reset passed.");
