"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { loadWebsite } = require("./browser-test-runtime.cjs");
loadWebsite();
const cases = JSON.parse(fs.readFileSync(path.join(__dirname, "test-fixtures/multiattack-sequences.json"), "utf8"));
const S = window.IRON_PIT_BROWSER_STATE, M = window.IRON_PIT_BROWSER_MULTIATTACK_CHOICES;
function setupFor(fixture) {
  const actor = { combatant_id: "actor", side: "monsters", state: S.buildState(structuredClone(fixture.actor)) };
  const target = { combatant_id: "target", side: "heroes", state: S.buildState(structuredClone(fixture.target)) };
  actor.state.position = { x: 6, y: 6 }; actor.state.formation_row = "back";
  target.state.position = { x: 6-fixture.distance/5, y: 6 };
  return { actor, target, setup: { heroes: [target], monsters: [actor], ruleset: "2014" } };
}
for (const fixture of cases) {
  const { actor, target, setup } = setupFor(fixture);
  const before = structuredClone(actor.state), calls = [];
  const roll = (sides) => { calls.push(sides); return sides === 20 ? 15 : 1; };
  window.IRON_PIT_DICE = { roll, rollMany: (n, sides) => Array.from({ length: n }, () => roll(sides)) };
  assert.equal(M.expectedDamage(actor, setup), fixture.score, fixture.id);
  assert.equal(M.selectSequence(actor, setup)?.variant.id ?? null, fixture.variant);
  assert.deepEqual(actor.state, before, "preview is pure");
  const result = window.IRON_PIT_BROWSER_MULTIATTACK.resolveAttackAction(1, 1, actor, setup);
  assert.deepEqual(result.events.filter((e) => e.event_type === "attack").map((e) => e.weapon_id), fixture.weapons);
  assert.deepEqual(calls, fixture.diceCalls);
  assert.equal(target.state.current_hp, fixture.remainingHp);
  assert.equal(actor.state.action_available, fixture.actionAvailable);
  assert.equal(actor.state.bonus_action_available, true);
  assert.deepEqual(actor.state.template, before.template);
  assert.equal(S.buildState(structuredClone(fixture.actor)).action_available, true);
  if (fixture.id === "gladiator-5") {
    assert.equal(actor.state.template.armor_class, 16);
    const twoHanded = actor.state.template.attacks.find((a) => a.id.endsWith("spear-two-handed"));
    assert.ok(twoHanded.unavailableReason);
    const fresh = setupFor(fixture), prior = structuredClone(fresh.actor.state);
    assert.throws(() => window.IRON_PIT_BROWSER_ATTACK.resolveAttack(1, 1, fresh.actor, fresh.target, twoHanded, 5), /unavailable/);
    assert.deepEqual(fresh.actor.state, prior);
  }
}
// Unselected corrupt branches must fail atomically, with no supported-prefix execution.
{
  const { actor, setup } = setupFor(cases[0]);
  actor.state.template.attack_action.variants[1].slots[0].attackIds = ["unbound"];
  const before = structuredClone(actor.state), originalError = console.error;
  console.error = () => {};
  try {
    assert.throws(() => window.IRON_PIT_BROWSER_MULTIATTACK.resolveAttackAction(1, 1, actor, setup), /Unknown Multiattack IDs/);
    assert.deepEqual(actor.state, before);
  } finally { console.error = originalError; }
}
{
  const { actor, setup } = setupFor(cases[0]);
  window.IRON_PIT_DICE = { roll: () => 1, rollMany: () => { throw new Error("Natural 1 must not roll damage."); } };
  const result = window.IRON_PIT_BROWSER_MULTIATTACK.resolveAttackAction(1, 1, actor, setup);
  assert.equal(result.events.filter((e) => e.event_type === "attack").length, 1);
  assert.equal(actor.state.turn_terminated, true);
}
assert.equal(cases.length, 6);
console.log("Source Multiattack counts, highest legal damage, fixed shield, interruption, reset, atomic validation, and Python/browser parity passed.");
