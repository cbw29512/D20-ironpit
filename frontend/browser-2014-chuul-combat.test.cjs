"use strict";

// Complete 2014 Chuul card: printed Multiattack → shared grapple → shared
// failed-save grouped conditions → one end-of-turn repeat save.
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

try {
  const card = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-chuul"];
  assert.ok(card, "Chuul must be present only when the full source is admitted");
  const template = structuredClone(card);
  assert.deepEqual(template.attack_action.slots.map(s => ({
    attacks: s.attackIds, saves: s.saveActionIds, held: Boolean(s.requiresSourceGrapple),
  })), [
    { attacks: ["2014-chuul-pincer"], saves: [], held: false },
    { attacks: ["2014-chuul-pincer"], saves: [], held: false },
    { attacks: [], saves: ["tentacles"], held: true },
  ]);
  const action = template.saving_throw_actions.find(a => a.id === "tentacles");
  assert.ok(action && action.requiresTargetGrappledBySource);
  assert.deepEqual(
    [action.dc, action.range, action.failedSaveTimedEffect.effectId,
      action.failedSaveTimedEffect.additionalEffectIds,
      action.failedSaveTimedEffect.durationRounds,
      action.failedSaveTimedEffect.repeatSaveTiming],
    [13, 10, "poisoned", ["paralyzed"], 10, "target_turn_end"],
  );

  const State = window.IRON_PIT_BROWSER_STATE;
  const Fighter = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-2014-l5"];
  assert.ok(Fighter);
  const member = (id, side, base) => ({
    combatant_id: id, side, position_ft: side === "monsters" ? 0 : 5,
    state: State.buildState(structuredClone(base)),
  });
  const actor = member("holder", "monsters", template);
  const victim = member("hero", "heroes", Fighter);
  const scene = { monsters: [actor], heroes: [victim] };
  const G = window.IRON_PIT_BROWSER_GRAPPLE;
  const M = window.IRON_PIT_BROWSER_MULTIATTACK;
  const V = window.IRON_PIT_BROWSER_SAVES;
  const L = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE;
  assert.equal(V.legalAction(action, victim, 5, actor.combatant_id, actor), false);
  const dice = window.IRON_PIT_DICE;
  const previousRoll = dice.roll;
  const previousMany = dice.rollMany;
  let d20 = 0;
  dice.roll = (sides) => sides === 20 ? (++d20 <= 2 ? 18 : 1) : 3;
  dice.rollMany = (count, sides) => Array.from({ length: count }, () => dice.roll(sides));
  try {
    const oldHP = victim.state.current_hp;
    const outcome = M.resolveAttackAction(1, 1, actor, scene);
    const attacks = outcome.events.filter(e => e.event_type === "attack");
    const saves = outcome.events.filter(e => e.feature_id === "tentacles");
    assert.equal(attacks.length, 2, "Two Pincer attacks are required");
    assert.equal(saves.length, 1, "At most one conditional Tentacles save");
    assert.equal(saves[0].save_succeeded, false);
    assert.ok(victim.state.current_hp < oldHP, "Pincer must deal its regular damage");
    assert.ok(victim.state.grapple_sources.some(g => g.source_id === "holder"));
    assert.ok(victim.state.active_effect_ids.includes("poisoned"));
    assert.ok(victim.state.active_effect_ids.includes("paralyzed"));
    assert.equal(actor.state.action_available, false);
    const first = victim.state.timed_effects.find(e => e.effect_id === "poisoned");
    assert.equal(first.expires_round, 11);
    assert.equal(first.repeat_save_timing, "target_turn_end");
    dice.roll = (sides) => sides === 20 ? 20 : 3;
    const ending = L.resolveTargetTiming(outcome.sequence, 2, victim, "target_turn_end", scene);
    assert.equal(ending.events.filter(e => e.feature_id === "tentacles").length, 1);
    assert.ok(!victim.state.active_effect_ids.includes("poisoned"));
    assert.ok(!victim.state.active_effect_ids.includes("paralyzed"));
    G.release(victim.state, "holder");
    assert.equal(V.legalAction(action, victim, 5, actor.combatant_id, actor), false);
  } finally {
    dice.roll = previousRoll;
    dice.rollMany = previousMany;
  }
  assert.deepEqual(card, template, "The source card never mutates");
  console.log("2014 Chuul complete Pincer/Tentacles conditional fight and repeat save passed");
} catch (error) {
  console.error("2014 Chuul end-to-end browser combat regression failed", error);
  process.exitCode = 1;
}
