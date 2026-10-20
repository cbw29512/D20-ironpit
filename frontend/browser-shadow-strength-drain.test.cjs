"use strict";

// Real browser attack path: card -> hit -> necrotic HP -> universal score loss.
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

const card = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-shadow"];
assert.ok(card, "Shadow must be admitted into the 2014 browser roster");
const attack = card.attacks.find((a) => a.name === "Strength Drain");
assert.ok(attack, "Shadow's printed action must be exported");
assert.equal(attack.bonus, 4);
assert.deepEqual([attack.diceCount, attack.diceSize, attack.damageBonus, attack.damageType],
  [2, 6, 2, "necrotic"]);
assert.deepEqual(attack.onHitAbilityScoreReduction, {
  source: "Strength Drain", ability: "strength", diceCount: 1, diceSize: 4,
});

const S = window.IRON_PIT_BROWSER_STATE;
const A = window.IRON_PIT_BROWSER_ATTACK;
const R = window.IRON_PIT_BROWSER_ABILITY_SCORE_REDUCTION;
const template = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-2014-l5"];
assert.ok(template, "A certified 2014 hero must be available");
const member = (id, side, cardTemplate, pos) => ({
  combatant_id: id, side, position_ft: pos,
  state: S.buildState(structuredClone(cardTemplate)),
});
const attacker = member("shadow", "monsters", card, 10);
const target = member("hero", "heroes", template, 5);
const setup = { ruleset: "2014", heroes: [target], monsters: [attacker] };
const originalCard = structuredClone(target.state.template.ability_scores);
const originalStrength = originalCard.strength;
assert.ok(originalStrength >= 6);

// Live fight state changes; never lower the original hero card's base score.
R.apply(target.state, "strength", originalStrength - 6);
target.state.current_hp = 100;
let nextD20 = 18;
window.IRON_PIT_DICE = {
  roll: (sides) => sides === 20 ? nextD20 : (sides === 4 ? 2 : 1),
  rollMany: (count, sides) => Array.from({ length: count },
    () => sides === 20 ? nextD20 : (sides === 4 ? 2 : 1)),
};
for (let index = 1; index <= 3; index++) {
  S.beginTurn(attacker.state);
  const hpBefore = target.state.current_hp;
  const event = A.resolveAttack(index, index, attacker, target, attack, 5, { setup });
  assert.equal(event.hit, true, "Successful hit must apply normal necrotic damage");
  assert.equal(event.attack_name, "Strength Drain");
  assert.ok(target.state.current_hp <= hpBefore, "HP damage cannot heal the target");
  assert.ok(event.description.includes("Strength Drain"), "Combat log must name source action");
  assert.equal(R.effectiveScore(target.state, "strength"), Math.max(0, 6 - index * 2));
  assert.deepEqual(target.state.template.ability_scores, originalCard,
    "No source card stat may mutate during the encounter");
}
assert.equal(target.state.is_dead, true, "Strength 0 must immediately kill a pregen");
assert.equal(target.state.death_save_failures || 0, 0);
assert.equal(target.state.death_save_successes || 0, 0);

const newFight = member("hero-next-fight", "heroes", template, 5);
assert.equal(R.effectiveScore(newFight.state, "strength"), originalStrength);
assert.deepEqual(newFight.state.ability_score_reductions, {});

const missTarget = member("hero-miss", "heroes", template, 5);
const freshShadow = member("shadow-miss", "monsters", card, 10);
const missSetup = { ruleset: "2014", heroes: [missTarget], monsters: [freshShadow] };
nextD20 = 1;
S.beginTurn(freshShadow.state);
const miss = A.resolveAttack(4, 1, freshShadow, missTarget, attack, 5, { setup: missSetup });
assert.equal(miss.hit, false, "A natural 1 misses regardless of attack bonus");
assert.equal(R.effectiveScore(missTarget.state, "strength"), originalStrength);
assert.deepEqual(missTarget.state.ability_score_reductions, {});
console.log("2014 Shadow actual browser attack/drain/death/reset parity passed.");
