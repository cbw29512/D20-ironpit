"use strict";
const assert = require("node:assert/strict");
const path = require("node:path");
const { execFileSync } = require("node:child_process");
require("./browser-test-runtime.cjs").loadWebsite();

// Compile the pinned source and its expected outcomes through the Python oracle.
const root = path.resolve(__dirname, "..");
const fixture = JSON.parse(execFileSync("python", ["scripts/erinyes_weapon_parity_fixture.py"], {
  cwd: root, env: { ...process.env, PYTHONPATH: path.join(root, "backend") }, encoding: "utf8",
}));
const S = window.IRON_PIT_BROWSER_STATE;
for (const item of fixture.cases) {
  const actor = { combatant_id: "archer", side: "monsters", position_ft: 20, state: S.buildState(item.actor) };
  const target = { combatant_id: "victim", side: "heroes", position_ft: 0, state: S.buildState(item.target) };
  const setup = { heroes: [target], monsters: [actor], ruleset: "2014" };
  const attack = item.actor.attacks.find(value => value.id === item.attackId);
  const originalCard = structuredClone(item.actor), originalTarget = structuredClone(item.target);
  const queue = [...item.rolls];
  const roll = sides => {
    assert.ok(queue.length, `${item.id}: no extra damage/save rolls are allowed.`);
    const value = queue.shift();
    assert.ok(value >= 1 && value <= sides);
    return value;
  };
  window.IRON_PIT_DICE = { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
  const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(1, 1, actor, target, attack, 20, { setup });
  assert.equal(event.attack_name, item.id === "renamed-character" ? "Prism Bolt" : "Longbow");
  assert.equal(event.damage_roll.total, item.expected.damage, item.id);
  assert.equal(target.state.current_hp, item.expected.hp, item.id);
  assert.equal(event.save_succeeded, item.expected.saveSucceeded, item.id);
  assert.deepEqual(target.state.active_effect_ids, item.expected.conditions, item.id);
  assert.deepEqual(event.damage_components.map(part => ({ type: part.damage_type, total: part.total,
    applied: part.applied_total })), item.expected.parts, item.id);
  assert.equal(queue.length, 0, item.id);
  S.beginTurn(target.state);
  assert.deepEqual(target.state.active_effect_ids, item.expected.conditions, "No invented recovery save/expiry.");
  assert.equal(target.state.timed_effects.length, 0);
  assert.deepEqual(S.buildState(item.target).active_effect_ids, [], "New fights clear the prior Poisoned state.");
  if (item.expected.conditions.includes("poisoned")) {
    const cleric = { combatant_id: "cleric", side: "heroes", position_ft: 0, state: S.buildState(fixture.cleric) };
    const cure = fixture.cleric.condition_removal_actions.find(value => value.id === "lesser-restoration");
    assert.ok(cure, "Canonical 2014 Cleric must supply its real Lesser Restoration action.");
    const before = cleric.state.resources["spell-slot-2"];
    const removed = window.IRON_PIT_BROWSER_CONDITION_REMOVAL.resolve(2, 1, cleric, target, cure, ["poisoned"], "1:cleric");
    assert.deepEqual(removed.removed_condition_ids, ["poisoned"]);
    assert.equal(target.state.active_effect_ids.includes("poisoned"), false);
    assert.equal(cleric.state.resources["spell-slot-2"], before - 1);
    assert.equal(cleric.state.action_available, false);
  }
  assert.deepEqual(item.actor, originalCard);
  assert.deepEqual(item.target, originalTarget);
}
assert.equal(fixture.cases.length, 5);
console.log("2014 included poison weapons: Python/browser source, saves, immunity, resistance, renamed character, cure and reset parity passed.");
