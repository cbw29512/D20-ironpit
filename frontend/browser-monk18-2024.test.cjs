"use strict";

const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

const template = structuredClone(window.IRON_PIT_BROWSER_HEROES["kael-stillwater-l18"]);
assert.ok(template, "generated 2024 Monk 18 card must exist");

assert.equal(template.level, 18);
assert.equal(template.max_hp, 147);
assert.equal(template.speed_ft, 60);
assert.equal(template.initiative_bonus, 11);
assert.equal(template.resources["focus-points"], 18);

const action = template.timed_self_buff_actions.find((item) => item.id === "superior-defense");
assert.ok(action, "Superior Defense must be exported");
assert.equal(action.activationTiming, "start_turn");
assert.equal(action.resourceId, "focus-points");
assert.equal(action.resourceCost, 3);
assert.equal(action.durationRounds, 10);
assert.equal(action.endsIfSourceIncapacitated, true);
assert.equal(action.damageResistances.includes("force"), false);

const S = window.IRON_PIT_BROWSER_STATE;
const B = window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS;
const hero = {
  combatant_id: "hero-kael-18",
  side: "heroes",
  position_ft: 5,
  state: S.buildState(template),
};
const target = {
  combatant_id: "target",
  side: "monsters",
  position_ft: 10,
  state: S.buildState(structuredClone(window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"])),
};
const setup = { heroes: [hero], monsters: [target] };

S.beginTurn(hero.state);
const beforeAction = hero.state.action_available;
const beforeBonus = hero.state.bonus_action_available;
assert.equal(window.IRON_PIT_BROWSER_PRECOMBAT_BUFFS.choose(hero, setup), null);
const choice = B.choose(hero, setup, "start_turn");
assert.ok(choice);
assert.equal(choice.id, "superior-defense");

const event = B.resolve(1, 1, hero, choice, {
  spendActionCost: false,
  affectedStates: [hero.state, target.state],
});
assert.equal(event.feature_id, "superior-defense");
assert.equal(event.resource_remaining, 15);
assert.equal(hero.state.action_available, beforeAction);
assert.equal(hero.state.bonus_action_available, beforeBonus);
assert.equal(hero.state.timed_effects[0].expires_round, 11);

assert.equal(window.IRON_PIT_BROWSER_ATTACK.adjustedDamage(hero.state, 9, "fire"), 4);
assert.equal(window.IRON_PIT_BROWSER_ATTACK.adjustedDamage(hero.state, 9, "psychic"), 4);
assert.equal(window.IRON_PIT_BROWSER_ATTACK.adjustedDamage(hero.state, 9, "force"), 9);

assert.equal(B.choose(hero, setup, "start_turn"), null);

console.log("2024 Monk 18 Superior Defense browser parity passed.");
