"use strict";
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();
const S = window.IRON_PIT_BROWSER_STATE, I = window.IRON_PIT_BROWSER_CONDITION_IMMUNITY;
const Q = window.IRON_PIT_BROWSER_CONDITION_RULES, A = window.IRON_PIT_BROWSER_ATTACK;
const card = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-bearded-devil"];
assert.ok(card, "The already-implemented Bearded Devil must reach the generated roster.");
const before = structuredClone(card);
assert.equal(card.passive_modifier_grants[0].source_name, "Steadfast");
assert.equal(card.passive_modifier_grants[0].required_visible_active_ally_within_ft, 30);
const beard = card.attacks.find(attack => attack.name === "Beard");
assert.equal(beard.onHitConditionSave.cannotRegainHitPoints, true);
assert.equal(beard.onHitConditionSave.repeatSaveTiming, "target_turn_end");
const member = (id, side, template, x) => {
  const state = S.buildState(template);
  state.position = { x, y: 1 };
  return { combatant_id: id, side, state, position_ft: x * 5 };
};
function encounter(template = card) {
  const owner = member("owner", "monsters", template, 1);
  const ally = member("ally", "monsters", window.IRON_PIT_BROWSER_MONSTERS_2014["2014-commoner"], 7);
  const foe = member("foe", "heroes", window.IRON_PIT_BROWSER_MONSTERS_2014["2014-adult-black-dragon"], 2);
  return { owner, ally, foe, setup: { heroes: [foe], monsters: [owner, ally], ruleset: "2014" } };
}
for (const [change, expected] of [["boundary", true], ["stunned", false], ["paralyzed", false],
  ["unconscious", false], ["distant", false], ["dead", false], ["zero-hp", false],
  ["invisible", false], ["blind-owner", false], ["enemy-only", false], ["self-only", false]]) {
  const { owner, ally, setup } = encounter();
  if (["stunned", "paralyzed", "unconscious", "invisible"].includes(change)) ally.state.active_effect_ids.push(change);
  if (change === "distant") ally.state.position.x = 8;
  if (change === "dead") ally.state.is_dead = true;
  if (change === "zero-hp") ally.state.current_hp = 0;
  if (change === "blind-owner") owner.state.active_effect_ids.push("blinded");
  if (["enemy-only", "self-only"].includes(change)) setup.monsters.pop();
  if (change === "self-only") setup.heroes.length = 0;
  assert.equal(I.immune(owner.state, "frightened", null, { actor: owner, setup }), expected, change);
  assert.equal(I.immune(owner.state, "charmed", null, { actor: owner, setup }), false);
}
const dice = values => {
  const roll = () => { assert.ok(values.length, "Unexpected extra die roll"); return values.shift(); };
  window.IRON_PIT_DICE = { roll, rollMany: count => Array.from({ length: count }, roll) };
};
for (const kind of ["monster", "character"]) {
  const renamed = structuredClone(card);
  Object.assign(renamed, { id: "crystal-warden", name: "Crystal Warden", kind, source_trait_names: ["Crystal Resolve"] });
  Object.assign(renamed.passive_modifier_grants[0], { source_id: "crystal-resolve", source_name: "Crystal Resolve" });
  const original = structuredClone(renamed);
  const { owner, ally, foe, setup } = encounter(renamed);
  const action = foe.state.template.saving_throw_actions.find(item => item.id === "frightful-presence");
  dice([1]);
  const blocked = window.IRON_PIT_BROWSER_SAVES.resolveAction(1, 1, foe, owner, action, 5, { spendAction: false, setup });
  assert.equal(blocked.save_succeeded, false);
  assert.deepEqual(blocked.applied_condition_ids, []);
  ally.state.position.x = 8;
  dice([1]);
  const landed = window.IRON_PIT_BROWSER_SAVES.resolveAction(2, 1, foe, owner, action, 5, { spendAction: false, setup });
  assert.deepEqual(landed.applied_condition_ids, ["frightened"]);
  assert.equal(Q.has(owner.state, "frightened", setup), true);
  assert.equal(A.conditionSources(owner.state, foe.state, 5, "foe", setup).disadvantage, 1);
  assert.equal(window.IRON_PIT_BROWSER_GRID_REACTION_SUPPORT.approachesFearSource(owner, { x: 2, y: 1 }, setup), true);
  ally.state.position.x = 7;
  assert.equal(Q.has(owner.state, "frightened", setup), false);
  assert.ok(owner.state.active_effect_ids.includes("frightened"), "Suppression must preserve the timed source.");
  assert.equal(A.conditionSources(owner.state, foe.state, 5, "foe", setup).disadvantage, 0);
  assert.equal(window.IRON_PIT_BROWSER_GRID_REACTION_SUPPORT.approachesFearSource(owner, { x: 2, y: 1 }, setup), false);
  dice([10, 1, 20]);
  const hit = A.resolveAttack(3, 1, owner, foe, renamed.attacks[0], 5, { spendAction: false, setup });
  assert.equal(hit.attack_roll.mode, "normal");
  ally.state.position.x = 8;
  assert.equal(Q.has(owner.state, "frightened", setup), true);
  const fresh = S.buildState(renamed);
  assert.deepEqual(fresh.active_effect_ids, []);
  assert.deepEqual(fresh.timed_effects, []);
  assert.equal(I.immune(fresh, "frightened"), false);
  assert.deepEqual(renamed, original);
}
assert.deepEqual(card, before);
require("node:vm").runInThisContext(require("node:fs").readFileSync(
  require("node:path").join(__dirname, "browser-turbo.js"), "utf8"));
const hero = Object.values(window.IRON_PIT_BROWSER_HEROES)
  .find(item => item.ruleset === "2014" && item.class_id === "fighter" && item.level === 5);
for (const count of [1, 2]) {
  const selection = { ruleset: "2014", hero_ids: Array(count).fill(hero.id), monster_ids: Array(count).fill(card.id) };
  const first = window.IRON_PIT_BROWSER_TURBO.runSeeded(selection, 20261019 + count).battle;
  const replay = window.IRON_PIT_BROWSER_TURBO.runSeeded(selection, 20261019 + count).battle;
  assert.deepEqual(first.events, replay.events);
  assert.equal(first.outcome, replay.outcome);
}
assert.deepEqual(card, before);
console.log("Bearded Devil source admission, visible active allies, dynamic fear suppression, renamed forms and replay passed.");
