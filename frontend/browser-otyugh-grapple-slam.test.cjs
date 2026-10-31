"use strict";
const assert = require("node:assert/strict");
try {
  require("./browser-test-runtime.cjs").loadWebsite();
  const source = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-otyugh"];
  assert.ok(source, "2014 Otyugh must be present only after source admission");
  const template = structuredClone(source);
  const action = template.saving_throw_actions.find(row => row.name === "Tentacle Slam");
  assert.ok(action, "Canonical 2014 source must export Tentacle Slam");
  assert.equal(action.requiresTargetGrappledBySource, true);
  assert.equal(action.targetScope, "all-other-creatures");
  assert.equal(action.dc, 14);
  assert.equal(action.maxTargets, 2);
  assert.equal(action.damageDiceCount, 2);
  assert.equal(action.damageDiceSize, 6);
  assert.equal(action.damageBonus, 3);
  assert.equal(action.failedSaveTimedEffect.effectId, "stunned");
  assert.equal(action.failedSaveTimedEffect.expiryTiming, "source_turn_end");
  const State = window.IRON_PIT_BROWSER_STATE;
  const G = window.IRON_PIT_BROWSER_GRAPPLE;
  const M = window.IRON_PIT_BROWSER_MULTI_SAVE_PROVIDER;
  const member = (id, side) => ({
    combatant_id: id, side, position_ft: 5,
    state: State.buildState(structuredClone(template)),
  });
  const actor = member("source", "monsters");
  const first = member("held-a", "heroes");
  const second = member("held-b", "heroes");
  const unrelated = member("unrelated", "heroes");
  for (const target of [first, second]) G.apply(target.state, "source", 13, 10, true);
  G.apply(unrelated.state, "different-source", 13, 10, true);
  const setup = { heroes: [first, second, unrelated], monsters: [actor] };
  const selection = M.choose(actor, setup);
  assert.ok(selection);
  assert.deepEqual(selection.targets.map(x => x.combatant_id), ["held-a", "held-b"]);
  const hp = [first, second, unrelated].map(x => x.state.current_hp);
  const rolls = [3, 4, 1, 20];
  const dice = window.IRON_PIT_DICE;
  const previousRoll = dice.roll;
  const previousMany = dice.rollMany;
  dice.roll = () => rolls.shift();
  dice.rollMany = (count) => Array.from({ length: count }, () => dice.roll());
  try {
    const result = M.resolve(1, 1, actor, setup, action, selection.targets);
    assert.equal(result.events.length, 2);
    assert.equal(first.state.current_hp, hp[0] - 10);
    assert.equal(second.state.current_hp, hp[1] - 5);
    assert.equal(unrelated.state.current_hp, hp[2]);
    assert.ok(first.state.active_effect_ids.includes("stunned"));
    assert.ok(!second.state.active_effect_ids.includes("stunned"));
    assert.equal(actor.state.action_available, false);
  } finally {
    dice.roll = previousRoll;
    dice.rollMany = previousMany;
  }
  G.release(first.state, "source");
  actor.state.action_available = true;
  assert.deepEqual(M.choose(actor, setup).targets.map(x => x.combatant_id), ["held-b"]);
  G.release(second.state, "source");
  assert.equal(M.choose(actor, setup), null);
  assert.deepEqual(source, template, "Source cards are immutable");
  console.log("2014 Otyugh source Slam real browser save/damage/Stunned passed.");
} catch (error) {
  console.error("Otyugh real-browser grapple Slam regression failed", error);
  throw error;
}
