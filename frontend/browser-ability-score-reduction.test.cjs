"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
for (const name of [
  "browser-terminal-effects.js", "browser-zero-hp.js", "browser-ability-score-reduction.js",
]) load(name);

const R = window.IRON_PIT_BROWSER_ABILITY_SCORE_REDUCTION;
const state = () => ({
  template: { name: "Arbitrary Target", kind: "monster",
    ability_scores: { strength: 6, dexterity: 14, constitution: 10,
      intelligence: 9, wisdom: 11, charisma: 8 } },
  current_hp: 25, is_dead: false, is_alive: true, is_unconscious: false,
  is_stable: false, concentration: null, replacement_form: null,
  active_effect_ids: [], ability_score_reductions: {},
});

{
  const target = state();
  const first = R.apply(target, "strength", 2, { zeroKills: true });
  assert.deepEqual(first, {
    ability: "strength", scoreBefore: 6, scoreAfter: 4,
    applied: 2, deathOutcome: null,
  });
  assert.equal(R.effectiveModifier(target, "strength"), -3);
  assert.equal(target.template.ability_scores.strength, 6, "source card remains unchanged");
  assert.equal(R.effectiveScore(state(), "strength"), 6, "new fight starts undrained");
  assert.equal(R.apply(target, "strength", 4, { zeroKills: true }).deathOutcome, "dead");
  assert.equal(target.is_dead, true);
  assert.equal(target.current_hp, 0);
  assert.equal(R.apply(target, "strength", 2, { zeroKills: true }).applied, 0);
}
{
  const target = state();
  assert.equal(R.apply(target, "strength", 100).scoreAfter, 0);
  assert.equal(target.is_dead, true);
  assert.throws(() => R.apply(target, "strength", -1), /Invalid ability reduction amount/);
  assert.throws(() => R.apply(target, "strength", 1.5), /Invalid ability reduction amount/);
  assert.throws(() => R.effectiveScore(target, "unknown"), /Unknown ability/);
}
{
  const hero = state();
  hero.template.kind = "hero";
  const zero = R.apply(hero, "strength", 6, { zeroKills: true });
  assert.equal(zero.scoreAfter, 0);
  assert.equal(zero.deathOutcome, "dead");
  assert.equal(hero.is_dead, true);
  assert.equal(hero.is_unconscious, false);
  assert.equal(hero.death_save_failures || 0, 0);
}
{
  const target = state();
  assert.equal(R.abilityModifierDelta(target, "strength"), 0);
  R.apply(target, "strength", 2);
  assert.equal(R.abilityModifierDelta(target, "strength"), -1);
  assert.equal(R.abilityModifierDelta(target, "dexterity"), 0);
  assert.equal(R.abilityModifierDelta(target, null), 0);
}
for (const ability of ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]) {
  for (const kind of ["hero", "monster"]) {
    const target = state();
    target.template.kind = kind;
    const original = target.template.ability_scores[ability];
    const result = R.apply(target, ability, original, { zeroKills: false });
    assert.equal(result.scoreAfter, 0, ability);
    assert.equal(result.deathOutcome, "dead", ability);
    assert.equal(target.is_dead, true);
    assert.equal(target.current_hp, 0);
    assert.equal(target.is_unconscious, false);
    assert.equal(target.death_save_failures || 0, 0);
    assert.equal(target.template.ability_scores[ability], original);
    const newFight = { ...target, template: target.template, is_dead: false, is_alive: true,
      current_hp: 25, ability_score_reductions: {} };
    assert.equal(R.effectiveScore(newFight, ability), original, "fresh battle starts from original card");
  }
}
{
  // This generic attack rider is attached to source cards by the serializer.
  // Rename its displayed ability without changing the underlying resolution.
  const target = state();
  const original = structuredClone(target.template.ability_scores);
  window.IRON_PIT_DICE = { rollMany: (count, sides) => {
    assert.equal(count, 1);
    assert.equal(sides, 4);
    return [2];
  } };
  const effect = { source: "Unrelated Homebrew", ability: "strength", diceCount: 1, diceSize: 4 };
  const first = R.applyOnHit(target, effect);
  const second = R.applyOnHit(target, { ...effect, source: "Strength Drain" });
  assert.deepEqual(first.rolls, [2]);
  assert.equal(second.scoreAfter, 2);
  assert.equal(target.ability_score_reductions.strength, 4);
  assert.deepEqual(target.template.ability_scores, original);
  assert.equal(R.applyOnHit(target, effect).deathOutcome, "dead");
  assert.equal(target.death_save_failures || 0, 0);
  assert.deepEqual(state().template.ability_scores, original, "future fight uses original card");
  assert.throws(() => R.applyOnHit(state(), { ...effect, diceSize: 0 }), /Invalid/);
}
load("browser-ability-checks.js");
{
  const checks = window.IRON_PIT_BROWSER_ABILITY_CHECKS;
  const roll = { total: 1, notation: "1d20", rolls: [1], modifier: 0, selected_roll: 1, revisions: [] };
  const target = state();
  target.template.ability_check_minimums = [{ source_id: "synthetic-floor", ability: "strength" }];
  assert.equal(checks.applyMinimum(target, "strength", roll).total, 6);
  R.apply(target, "strength", 2);
  const drained = checks.applyMinimum(target, "strength", roll);
  assert.equal(drained.total, 4);
  assert.equal(drained.revisions[0].replacement_total, 4);
  assert.equal(target.template.ability_scores.strength, 6);
  assert.equal(checks.applyMinimum(state(), "strength", roll).total, 1);
  const dex = state();
  dex.template.ability_check_minimums = [{ source_id: "renamed-floor", ability: "dexterity" }];
  R.apply(dex, "dexterity", 2);
  assert.equal(checks.applyMinimum(dex, "dexterity", roll).total, 12);
  assert.equal(dex.template.ability_scores.dexterity, 14);
}
console.log("Universal browser ability-score reduction parity passed.");
