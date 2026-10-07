"use strict";
const assert = require("node:assert/strict"), fs = require("node:fs"), path = require("node:path");
const { loadWebsite } = require("./browser-test-runtime.cjs");
loadWebsite();
const cases = JSON.parse(fs.readFileSync(path.join(__dirname, "test-fixtures/grick-sequence.json"), "utf8"));
const S = window.IRON_PIT_BROWSER_STATE, M = window.IRON_PIT_BROWSER_MULTIATTACK_CHOICES;
for (const fixture of cases) {
  const actor = { combatant_id: "actor", side: "monsters", state: S.buildState(structuredClone(fixture.actor)) };
  const targets = ["target", "other"].map(id => ({ combatant_id: id, side: "heroes", state: S.buildState(structuredClone(fixture.target)) }));
  actor.state.position = { x: 6, y: 6 };
  targets.forEach(t => { t.state.position = { x: 6-fixture.distance/5, y: 6 }; t.state.formation_row = "front"; });
  targets[0].state.current_hp = fixture.initialHp;
  const setup = { heroes: targets, monsters: [actor], ruleset: "2014" }, before = structuredClone([actor, ...targets]), calls = [];
  const roll = sides => { calls.push(sides); return sides === 20 ? (calls.filter(s => s === 20).length === 1 ? fixture.firstRoll : 15) : 1; };
  window.IRON_PIT_DICE = { roll, rollMany: (n, sides) => Array.from({ length: n }, () => roll(sides)) };
  assert.equal(M.expectedDamage(actor, setup), fixture.score, fixture.id);
  assert.deepEqual([actor, ...targets], before, "preview stays pure");
  const A = window.IRON_PIT_BROWSER_ATTACK, D = window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH;
  const originalAttack = A.resolveAttack, originalChain = D.chain;
  A.resolveAttack = (sequence, round, member, target, attack, distance, extra) => originalAttack(sequence, round, member,
    fixture.redirectFirst && attack.id.endsWith("tentacles") ? targets[1] : target, attack, distance, extra);
  D.chain = (sequence, round, member, event, encounter, turnKey) => {
    if (event.weapon_id?.endsWith("tentacles")) {
      if (fixture.afterFirst === "reorder") targets[0].state.formation_row = "back";
      if (fixture.afterFirst === "move") targets[0].state.position = { x: 1, y: 6 };
    }
    return originalChain(sequence, round, member, event, encounter, turnKey);
  };
  let result;
  try { result = window.IRON_PIT_BROWSER_MULTIATTACK.resolveAttackAction(1, 1, actor, setup); }
  finally { A.resolveAttack = originalAttack; D.chain = originalChain; }
  const attacks = result.events.filter(e => e.event_type === "attack");
  assert.deepEqual(attacks.map(e => e.weapon_id), fixture.weapons, fixture.id);
  assert.deepEqual(attacks.map(e => e.target_id), fixture.targetIds, fixture.id);
  assert.deepEqual(calls, fixture.diceCalls, fixture.id);
  assert.deepEqual(targets.map(t => t.state.current_hp), fixture.remainingHp, fixture.id);
  assert.equal(actor.state.action_available, fixture.actionAvailable);
  assert.equal(actor.state.bonus_action_available, fixture.bonusActionAvailable);
  assert.equal(actor.state.turn_terminated, fixture.turnTerminated);
  assert.deepEqual(actor.state.template, before[0].state.template);
  const fresh = S.buildState(structuredClone(fixture.actor));
  assert.equal(fresh.action_available, true); assert.equal(fresh.turn_terminated, false);
}
// Invalid conditions fail before preview, costs, dice, or supported-prefix execution.
for (const corrupt of [s => { s[0].previousAttack = { hit: true, sameTarget: true }; },
  s => { s[1].previousAttack = { hit: "true" }; }, s => { s[1].previousAttack = {}; },
  s => { s[1].previousAttack = { hit: true, unknown: true }; }]) {
  const f = cases[0], actor = { combatant_id: "actor", side: "monsters", state: S.buildState(structuredClone(f.actor)) };
  corrupt(actor.state.template.attack_action.variants[0].slots);
  const before = structuredClone(actor.state), error = console.error;
  console.error = () => {};
  try { assert.throws(() => M.selectSequence(actor, { heroes: [], monsters: [actor], ruleset: "2014" }), /previous-attack|Previous-attack/); }
  finally { console.error = error; }
  assert.deepEqual(actor.state, before);
}
assert.equal(cases.length, 8);
console.log("Grick hit-dependent same-target follow-up: source, miss, natural 1, death, movement, retarget prevention, redirected target, reset and Python/browser parity passed.");
