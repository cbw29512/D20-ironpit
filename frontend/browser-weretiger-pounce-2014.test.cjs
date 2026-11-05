"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
require("./browser-test-runtime.cjs").loadWebsite();

const roster = window.IRON_PIT_BROWSER_MONSTERS_2014;
const card = roster["2014-weretiger"];
assert.ok(card, "Weretiger must enter the generated 2014 browser roster.");
const before = structuredClone(card);
const claw = card.attacks.find(item => item.id === "2014-weretiger-claw-tiger-or-hybrid-form-only");
assert.deepEqual(claw.charge, {
  minimumMove: 15,
  proneSaveAbility: "strength",
  proneSaveDc: 14,
  followUpAttackId: "2014-weretiger-bite-tiger-or-hybrid-form-only",
  followUpRequiredTargetCondition: "prone",
  followUpActionCost: "bonus_action",
});

const actor = { side: "monsters", combatant_id: card.id, state: {
  action_available: true, bonus_action_available: true, active_effect_ids: [],
  is_dead: false, is_unconscious: false, initiative_total: 20,
  turn_terminated: false, template: { ...card, speed_ft: 40 },
}};
const defender = { side: "heroes", combatant_id: "prey", state: {
  active_effect_ids: [], initiative_total: 10, is_alive: true, is_dead: false,
  is_unconscious: false, current_hp: 500, template: { id: "prey" },
}};
const setup = { heroes: [defender], monsters: [actor] };
const originalResolve = window.IRON_PIT_BROWSER_ATTACK.resolveAttack;
const calls = [];
window.IRON_PIT_BROWSER_ATTACK.resolveAttack = (sequence, round, source, target, attack) => {
  calls.push(attack.id);
  if (calls.length === 1) target.state.active_effect_ids.push("prone");
  return { sequence, actor_id: source.combatant_id, hit: true,
    target_id: target.combatant_id, damage_roll: null };
};
window.IRON_PIT_BROWSER_CHARGE.resolveClosing(1, 1, actor, defender, setup);
assert.deepEqual(calls, [
  "2014-weretiger-claw-tiger-or-hybrid-form-only",
  "2014-weretiger-bite-tiger-or-hybrid-form-only",
]);
assert.equal(actor.state.bonus_action_available, false);
window.IRON_PIT_BROWSER_ATTACK.resolveAttack = originalResolve;
assert.deepEqual(card, before, "Fight state must not mutate the immutable source card.");
assert.equal(window.IRON_PIT_BROWSER_STATE.buildState(card).bonus_action_available, true,
  "A fresh fight resets the Pounce follow-up action economy.");

vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-turbo.js"), "utf8"),
  { filename: "browser-turbo.js" });
const hero = Object.values(window.IRON_PIT_BROWSER_HEROES)
  .find(item => item.ruleset === "2014" && item.class_id === "fighter" && item.level === 5);
assert.ok(hero);
for (const count of [1, 6]) {
  const selection = { ruleset: "2014", hero_ids: Array(count).fill(hero.id),
    monster_ids: Array(count).fill(card.id) };
  const seed = 20261105 + count;
  const first = window.IRON_PIT_BROWSER_TURBO.runSeeded(selection, seed).battle;
  const replay = window.IRON_PIT_BROWSER_TURBO.runSeeded(selection, seed).battle;
  assert.deepEqual(first.events, replay.events, `${count}v${count} must replay identically.`);
  assert.equal(first.outcome, replay.outcome);
  assert.equal(first.setup.monsters.length, count);
  assert.deepEqual(card, before);
}

console.log("2014 Weretiger source-qualified Pounce and deterministic fights passed.");
