"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), {filename: name},
);
const calls = [];
let outcomes = {high: false, low: true};
window.IRON_PIT_BROWSER_SPELL_INTERRUPT = {
  legal: (actor, caster) => actor.side !== caster.side && actor.state.reaction_available,
  resolve: (_sequence, _round, actor) => {
    calls.push(actor.combatant_id);
    assert.equal(actor.state.slots, 1);
    actor.state.reaction_available = false;
    actor.state.slots--;
    return [{actor_id: actor.combatant_id}, outcomes[actor.combatant_id]];
  },
};
load("browser-spell-interrupt-priority.js");
const dispatch = window.IRON_PIT_BROWSER_SPELL_INTERRUPT_PRIORITY.dispatch;
function scenario() {
  const member = (id, side) => ({
    combatant_id: id, side,
    state: {reaction_available: true, slots: 1},
  });
  const high = member("high", "heroes"), low = member("low", "heroes");
  const caster = member("caster", "monsters");
  const setup = {heroes: [high, low], monsters: [caster]};
  const action = {
    id: "counterspell", name: "Counterspell", printedLevel: 3,
    trigger: "visible_spell_cast", range: 60, castingAbility: "intelligence",
  };
  return {high, low, caster, setup, actions: {high: [action], low: [action]}};
}
try {
  {
    calls.length = 0; outcomes = {high: false, low: true};
    const {high, low, caster, setup, actions} = scenario();
    const result = dispatch(7, 2, caster, setup,
      ["high", "caster", "low"], actions, "Fireball", 3, true);
    assert.equal(result.stopped, true);
    assert.equal(result.sequence, 9);
    assert.deepEqual(result.events.map((e) => e.actor_id), ["high", "low"]);
    assert.deepEqual(calls, ["high", "low"]);
    assert.equal(high.state.slots, 0);
    assert.equal(low.state.slots, 0);
  }
  {
    calls.length = 0; outcomes = {high: true, low: true};
    const {low, caster, setup, actions} = scenario();
    const result = dispatch(7, 2, caster, setup,
      ["high", "low", "caster"], actions, "Blight", 4, true);
    assert.equal(result.stopped, true);
    assert.deepEqual(calls, ["high"]);
    assert.equal(result.sequence, 8);
    assert.equal(low.state.slots, 1);
    assert.equal(low.state.reaction_available, true);
  }
  for (const invalid of [
    ["high", "caster"], ["high", "high", "caster"],
    ["high", "low", "unknown"],
  ]) {
    calls.length = 0;
    const {high, low, caster, setup, actions} = scenario();
    assert.throws(() => dispatch(7, 2, caster, setup,
      invalid, actions, "Blight", 4, true));
    assert.deepEqual(calls, []);
    assert.equal(high.state.slots, 1);
    assert.equal(low.state.slots, 1);
  }
  {
    calls.length = 0;
    const {high, low, caster, setup, actions} = scenario();
    const result = dispatch(7, 2, caster, setup,
      ["high", "low", "caster"], actions, "Fire Breath", 0, false);
    assert.equal(result.stopped, false);
    assert.equal(result.sequence, 7);
    assert.deepEqual(calls, []);
    assert.equal(high.state.slots, 1);
    assert.equal(low.state.slots, 1);
  }
  console.log("Universal initiative-ordered Counterspell decision parity passed");
} catch (error) {
  console.error("Counterspell reaction decision-order regression failed", error);
  process.exitCode = 1;
}
