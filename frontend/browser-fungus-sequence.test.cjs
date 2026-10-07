"use strict";
const assert = require("node:assert/strict"), fs = require("node:fs"), path = require("node:path");
const { loadWebsite } = require("./browser-test-runtime.cjs");
loadWebsite();
const cases = JSON.parse(fs.readFileSync(path.join(__dirname, "test-fixtures/fungus-sequence.json"), "utf8"));
const S = window.IRON_PIT_BROWSER_STATE, M = window.IRON_PIT_BROWSER_MULTIATTACK_CHOICES;
for (const f of cases) {
  const actor = { combatant_id: "actor", side: "monsters", state: S.buildState(structuredClone(f.actor)) };
  const targets = ["target", "other"].map(id => ({ combatant_id: id, side: "heroes", state: S.buildState(structuredClone(f.target)) }));
  actor.state.position = { x: 6, y: 6 };
  targets.forEach(t => { t.state.position = { x: 6-f.distance/5, y: 6 }; });
  targets[0].state.current_hp = f.initialHp;
  const setup = { heroes: targets, monsters: [actor], ruleset: "2014" }, before = structuredClone([actor, ...targets]), calls = [];
  const roll = sides => {
    if (sides === 4) assert.equal(actor.state.action_available, false, "Action spent before repetition roll");
    calls.push(sides); return sides === 4 ? f.count : sides === 20 ? f.attackRoll : 1;
  };
  window.IRON_PIT_DICE = { roll, rollMany: (n, sides) => Array.from({ length: n }, () => roll(sides)) };
  assert.equal(M.expectedDamage(actor, setup), f.score, f.id);
  assert.deepEqual([actor, ...targets], before); assert.deepEqual(calls, []);
  const result = window.IRON_PIT_BROWSER_MULTIATTACK.resolveAttackAction(1, 1, actor, setup);
  const attacks = result.events.filter(e => e.event_type === "attack"), repetitions = result.events.filter(e => e.feature_roll);
  assert.deepEqual(attacks.map(e => e.weapon_id), f.weapons, f.id);
  assert.deepEqual(attacks.map(e => e.target_id), f.targetIds, f.id);
  assert.equal(repetitions.length, f.repetitionRoll ? 1 : 0);
  assert.deepEqual(repetitions[0]?.feature_roll ?? null, f.repetitionRoll);
  if (repetitions.length) {
    assert.ok(repetitions[0].sequence < attacks[0].sequence);
    assert.equal(repetitions[0].audit.steps[0].phase, "roll");
  }
  assert.deepEqual(calls, f.diceCalls);
  assert.deepEqual(targets.map(t => t.state.current_hp), f.remainingHp);
  assert.equal(actor.state.action_available, f.actionAvailable);
  assert.equal(actor.state.bonus_action_available, f.bonusActionAvailable);
  assert.equal(actor.state.turn_terminated, f.turnTerminated);
  assert.deepEqual(actor.state.template, before[0].state.template);
  const fresh = S.buildState(structuredClone(f.actor));
  assert.equal(fresh.action_available, true); assert.equal(fresh.turn_terminated, false);
}
for (const r of [{ diceCount: true, diceSize: 4 }, { diceCount: 1, diceSize: 9 },
  { diceCount: 3, diceSize: 4 }, { diceCount: 1, diceSize: 4, unknown: true }]) {
  const actor = { combatant_id: "actor", side: "monsters", state: S.buildState(structuredClone(cases[0].actor)) };
  actor.state.template.attack_action.variants[0].repetitions = r;
  const before = structuredClone(actor.state), error = console.error;
  console.error = () => {};
  try { assert.throws(() => M.selectSequence(actor, { heroes: [], monsters: [actor], ruleset: "2014" }), /random sequence repetition/); }
  finally { console.error = error; }
  assert.deepEqual(actor.state, before);
}
assert.equal(cases.length, 7);
console.log("Violet Fungus d4 counts 1–4, one logged roll/Action, interruption, retarget, no-range no-spend, fresh reset and Python/browser parity passed.");
