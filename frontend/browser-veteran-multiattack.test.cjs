"use strict";
const assert = require("node:assert/strict"), fs = require("node:fs"), path = require("node:path");
const { loadWebsite } = require("./browser-test-runtime.cjs");
loadWebsite();
const cases = JSON.parse(fs.readFileSync(path.join(__dirname, "test-fixtures/veteran-multiattack.json"), "utf8"));
const S = window.IRON_PIT_BROWSER_STATE, M = window.IRON_PIT_BROWSER_MULTIATTACK_CHOICES;
for (const fixture of cases) {
  const actor = { combatant_id: "actor", side: "monsters", state: S.buildState(structuredClone(fixture.actor)) };
  const target = { combatant_id: "target", side: "heroes", state: S.buildState(structuredClone(fixture.target)) };
  actor.state.position = { x: 6, y: 6 }; actor.state.formation_row = "back";
  target.state.position = { x: 6-fixture.distance/5, y: 6 };
  const setup = { heroes: [target], monsters: [actor], ruleset: "2014" }, before = structuredClone(actor.state), calls = [];
  const roll = (sides) => { calls.push(sides); return sides === 20 ? 15 : 1; };
  window.IRON_PIT_DICE = { roll, rollMany: (n, sides) => Array.from({ length: n }, () => roll(sides)) };
  assert.equal(M.expectedDamage(actor, setup), fixture.score);
  assert.equal(M.selectSequence(actor, setup)?.variant.id ?? null, fixture.variant);
  assert.deepEqual(actor.state, before);
  const result = window.IRON_PIT_BROWSER_MULTIATTACK.resolveAttackAction(1, 1, actor, setup);
  assert.deepEqual(result.events.filter(e => e.event_type === "attack").map(e => e.weapon_id), fixture.weapons);
  assert.deepEqual(calls, fixture.diceCalls);
  assert.equal(target.state.current_hp, fixture.remainingHp);
  assert.equal(actor.state.action_available, fixture.actionAvailable);
  assert.equal(actor.state.bonus_action_available, true);
  assert.deepEqual(actor.state.template, before.template);
  assert.equal(S.buildState(structuredClone(fixture.actor)).action_available, true);
  const two = actor.state.template.attacks.find(a => a.id.endsWith("longsword-two-handed"));
  assert.ok(two.unavailableReason);
  if (fixture.distance === 20) {
    const choice = window.IRON_PIT_BROWSER_FORMATION.chooseStandardAttack(actor, setup);
    assert.ok(choice.attack.id.endsWith("heavy-crossbow"));
    const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(1, 1, actor, target, choice.attack, 20, { setup });
    assert.equal(event.damage_roll.total, 2);
    assert.deepEqual(calls, [20, 10]);
    assert.equal(actor.state.action_available, false);
  }
}
assert.equal(cases.length, 4);
console.log("Both Veterans: printed three-sword sequence, fixed offhand, single crossbow fallback and Python/browser parity passed.");
