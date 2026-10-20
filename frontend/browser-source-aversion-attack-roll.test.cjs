"use strict";
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();
const S = window.IRON_PIT_BROWSER_STATE;
const A = window.IRON_PIT_BROWSER_ATTACK;
const V = window.IRON_PIT_BROWSER_VISUAL_SOURCE_AVERSION;
const card = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-commoner"];
assert.ok(card, "Actual immutable 2014 Commoner card must be available.");
const initialCard = structuredClone(card);
const actor = { combatant_id: "observer", side: "heroes", state: S.buildState(card) };
const source = { combatant_id: "gaze-source", side: "monsters", state: S.buildState(card) };
const other = { combatant_id: "other-target", side: "monsters", state: S.buildState(card) };
actor.state.position = { x: 6, y: 6 };
source.state.position = { x: 5, y: 6 };
other.state.position = { x: 6, y: 5 };
const setup = { heroes: [actor], monsters: [source, other], ruleset: "2014" };
actor.state.turns_started = 1;
actor.state.visual_aversion_windows = V.record(actor.state.visual_aversion_windows,
  "observer", "gaze-source", actor.state.turns_started);
window.IRON_PIT_DICE = {
  roll: sides => sides === 20 ? 15 : 1,
  rollMany: (count, sides) => Array.from({ length: count }, () => sides === 20 ? 15 : 1),
};
const strike = card.attacks[0];
const first = A.resolveAttack(1, 1, actor, source, strike, 5, { setup, spendAction: false });
assert.equal(first.attack_roll.mode, "disadvantage",
  "Aversion must disadvantage attacks against its single source.");
const second = A.resolveAttack(2, 1, actor, other, strike, 5, { setup, spendAction: false });
assert.equal(second.attack_roll.mode, "normal",
  "Aversion must not impose Blinded disadvantage on unrelated targets.");
actor.state.turns_started = 2;
const expired = A.resolveAttack(3, 2, actor, source, strike, 5, { setup, spendAction: false });
assert.equal(expired.attack_roll.mode, "normal",
  "Aversion ends at the start of the observer's next turn.");
const fresh = S.buildState(card);
assert.deepEqual(fresh.visual_aversion_windows, [], "New fights discard fight-only aversion.");
assert.deepEqual(card, initialCard, "Combat never edits the printed card.");
console.log("Source-neutral gaze aversion attack disadvantages: source, unrelated target, expiry and reset passed.");
