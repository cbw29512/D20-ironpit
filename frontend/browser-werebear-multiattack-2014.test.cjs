"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
require("./browser-test-runtime.cjs").loadWebsite();

const S = window.IRON_PIT_BROWSER_STATE;
const M = window.IRON_PIT_BROWSER_MULTIATTACK;
const C = window.IRON_PIT_BROWSER_MULTIATTACK_CHOICES;
const card = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-werebear"];
assert.ok(card, "Source-complete Werebear must enter the certified 2014 browser roster.");
const cardBefore = structuredClone(card);
assert.deepEqual(card.attack_action.variants.map(variant => ({
  kind: variant.attackKind,
  slots: variant.slots.map(slot => slot.attackIds),
})), [
  { kind: "melee", slots: [["2014-werebear-claw-bear-or-hybrid-form-only"],
    ["2014-werebear-claw-bear-or-hybrid-form-only"]] },
  { kind: "melee", slots: [["2014-werebear-greataxe-humanoid-or-hybrid-form-only"],
    ["2014-werebear-greataxe-humanoid-or-hybrid-form-only"]] },
]);

const actor = { combatant_id: "werebear", side: "monsters", state: S.buildState(card) };
const targetCard = structuredClone(window.IRON_PIT_BROWSER_MONSTERS_2014["2014-commoner"]);
targetCard.max_hp = 200;
const target = { combatant_id: "target", side: "heroes",
  state: S.buildState(targetCard) };
actor.state.position = { x: 6, y: 6 };
target.state.position = { x: 5, y: 6 };
const setup = { heroes: [target], monsters: [actor], ruleset: "2014" };
const roll = sides => sides === 20 ? 15 : 1;
window.IRON_PIT_DICE = { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
assert.deepEqual(C.selectSequence(actor, setup).variant.slots.map(slot => slot.attackIds), [
  ["2014-werebear-claw-bear-or-hybrid-form-only"],
  ["2014-werebear-claw-bear-or-hybrid-form-only"],
]);
const attacks = M.resolveAttackAction(1, 1, actor, setup).events.filter(event => event.event_type === "attack");
assert.deepEqual(attacks.map(event => event.attack_name), ["Claw (Bear or Hybrid Form Only)", "Claw (Bear or Hybrid Form Only)"]);
assert.deepEqual(card, cardBefore, "Fight-local selection must not mutate the immutable card.");
assert.equal(S.buildState(card).action_available, true, "A new fight resets mutable action state.");

vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-turbo.js"), "utf8"),
  { filename: "browser-turbo.js" });
const hero = Object.values(window.IRON_PIT_BROWSER_HEROES)
  .find(item => item.ruleset === "2014" && item.class_id === "fighter" && item.level === 5);
assert.ok(hero);
for (const count of [1, 6]) {
  const selection = { ruleset: "2014", hero_ids: Array(count).fill(hero.id),
    monster_ids: Array(count).fill(card.id) };
  const first = window.IRON_PIT_BROWSER_TURBO.runSeeded(selection, 20261104 + count).battle;
  const replay = window.IRON_PIT_BROWSER_TURBO.runSeeded(selection, 20261104 + count).battle;
  assert.deepEqual(first.events, replay.events, `${count}v${count} must replay identically.`);
  assert.equal(first.outcome, replay.outcome);
  assert.equal(first.setup.monsters.length, count);
  assert.deepEqual(card, cardBefore);
}

console.log("2014 Werebear repeated-choice Multiattack and deterministic full fights passed.");
