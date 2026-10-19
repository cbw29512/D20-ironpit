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
  assert.equal(R.apply(target, "strength", 100).scoreAfter, 1);
  assert.equal(target.is_dead, false);
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
console.log("Universal browser ability-score reduction parity passed.");
