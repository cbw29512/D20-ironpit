"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
require("./browser-test-runtime.cjs").loadWebsite();

const S = window.IRON_PIT_BROWSER_STATE;
const M = window.IRON_PIT_BROWSER_MULTIATTACK;
const C = window.IRON_PIT_BROWSER_MULTIATTACK_CHOICES;
const newlyAdmitted = ["werewolf", "wereboar", "wererat"];
const cards = newlyAdmitted.map(id => {
  const card = window.IRON_PIT_BROWSER_MONSTERS_2014[`2014-${id}`];
  assert.ok(card, `${id} must enter the generated 2014 browser roster.`);
  assert.ok(card.attack_action, `${id} must retain its compiled Multiattack.`);
  return card;
});
const before = new Map(cards.map(card => [card.id, structuredClone(card)]));

const targetCard = structuredClone(window.IRON_PIT_BROWSER_MONSTERS_2014["2014-commoner"]);
targetCard.max_hp = 500;
const roll = sides => sides === 20 ? 15 : 1;
window.IRON_PIT_DICE = {
  roll,
  rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)),
};

for (const card of cards) {
  const actor = { combatant_id: card.id, side: "monsters", state: S.buildState(card) };
  const target = { combatant_id: `target-${card.id}`, side: "heroes",
    state: S.buildState(targetCard) };
  actor.state.position = { x: 6, y: 6 };
  target.state.position = { x: 5, y: 6 };
  const setup = { heroes: [target], monsters: [actor], ruleset: "2014" };
  const sequence = C.selectSequence(actor, setup);
  assert.ok(sequence, `${card.name} must choose a legal source sequence.`);
  assert.equal(sequence.variant.slots.length, 2);
  const attacks = M.resolveAttackAction(1, 1, actor, setup).events
    .filter(event => event.event_type === "attack");
  assert.equal(attacks.length, 2, `${card.name} must resolve both printed attacks.`);
  assert.deepEqual(card, before.get(card.id), "Fight state must not mutate source cards.");
  assert.equal(S.buildState(card).action_available, true, "A fresh fight resets Action state.");
}

vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-turbo.js"), "utf8"),
  { filename: "browser-turbo.js" });
const hero = Object.values(window.IRON_PIT_BROWSER_HEROES)
  .find(item => item.ruleset === "2014" && item.class_id === "fighter" && item.level === 5);
assert.ok(hero);
for (const card of cards) {
  for (const count of [1, 6]) {
    const selection = { ruleset: "2014", hero_ids: Array(count).fill(hero.id),
      monster_ids: Array(count).fill(card.id) };
    const seed = 20261104 + count + card.id.length;
    const first = window.IRON_PIT_BROWSER_TURBO.runSeeded(selection, seed).battle;
    const replay = window.IRON_PIT_BROWSER_TURBO.runSeeded(selection, seed).battle;
    assert.deepEqual(first.events, replay.events,
      `${card.name} ${count}v${count} must replay identically.`);
    assert.equal(first.outcome, replay.outcome);
    assert.equal(first.setup.monsters.length, count);
    assert.deepEqual(card, before.get(card.id));
  }
}

console.log("2014 form-qualified Multiattack actions and deterministic full fights passed.");
