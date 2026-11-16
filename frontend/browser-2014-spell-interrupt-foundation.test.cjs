"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), {filename: name},
);
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state) => Boolean(state.reaction_available),
  spend: (state) => {state.reaction_available = false;},
};
window.IRON_PIT_BROWSER_CONDITION_RULES = {canSee: () => true};
window.IRON_PIT_BROWSER_STATE = {distance: (a, b) => Math.abs(a.position_ft - b.position_ft)};
let nextRoll = 1;
window.IRON_PIT_BROWSER_ROLLS = {d20: (bonus) => ({
  notation: "1d20", rolls: [nextRoll], selected_roll: nextRoll,
  total: nextRoll + bonus, modifier: bonus, mode: "normal",
})};
window.IRON_PIT_BROWSER_ABILITY_CHECKS = {
  mode: () => "normal",
  resolve: (_state, _ability, roll, dc) => ({roll, succeeded: roll.total >= dc}),
};
load("browser-spell-interrupt.js");
const R = window.IRON_PIT_BROWSER_SPELL_INTERRUPT;
const action = {
  id: "counterspell", name: "Counterspell", printedLevel: 3,
  range: 60, castingAbility: "intelligence", resourcePrefix: "spell-slot-",
  allowsHigherSlots: true,
};
function fixture(slots) {
  const actor = {
    combatant_id: "actor", side: "heroes", position_ft: 0,
    state: {
      reaction_available: true, is_alive: true, is_dead: false,
      resources: {...slots}, template: {
        name: "Interrupting caster", ability_scores: {intelligence: 10},
      },
    },
  };
  const caster = {
    combatant_id: "caster", side: "monsters", position_ft: 30,
    state: {
      reaction_available: true, is_alive: true, is_dead: false,
      template: {name: "Enemy caster"},
    },
  };
  return {actor, caster, setup: {heroes: [actor], monsters: [caster]}};
}
try {
  {
    const {actor, caster, setup} = fixture({"spell-slot-3": 1, "spell-slot-4": 1});
    assert.equal(R.slot(actor, action, 4), 4);
    const [event, interrupted] = R.resolve(
      1, 1, actor, caster, setup, action, "Blight", 4, true,
    );
    assert.equal(interrupted, true);
    assert.equal(event.ability_check_roll, null);
    assert.equal(actor.state.reaction_available, false);
    assert.equal(actor.state.resources["spell-slot-3"], 1);
    assert.equal(actor.state.resources["spell-slot-4"], 0);
  }
  for (const [die, succeeds] of [[1, false], [20, true]]) {
    const {actor, caster, setup} = fixture({"spell-slot-3": 1});
    nextRoll = die;
    const [event, interrupted] = R.resolve(
      2, 1, actor, caster, setup, action, "Blight", 4, true,
    );
    assert.equal(interrupted, succeeds);
    assert.equal(event.check_succeeded, succeeds);
    assert.equal(event.check_dc, 14);
    assert.equal(actor.state.resources["spell-slot-3"], 0);
  }
  for (const reason of ["nonspell", "friendly", "range", "reaction", "slot", "unseen"]) {
    const {actor, caster, setup} = fixture({"spell-slot-3": 1});
    const priorSight = window.IRON_PIT_BROWSER_CONDITION_RULES.canSee;
    try {
      if (reason === "friendly") caster.side = "heroes";
      if (reason === "range") caster.position_ft = 65;
      if (reason === "reaction") actor.state.reaction_available = false;
      if (reason === "slot") actor.state.resources["spell-slot-3"] = 0;
      if (reason === "unseen") window.IRON_PIT_BROWSER_CONDITION_RULES.canSee = () => false;
      const spellCast = reason !== "nonspell";
      assert.equal(R.legal(actor, caster, action, 3, spellCast), false, reason);
      assert.throws(() => R.resolve(
        3, 1, actor, caster, setup, action, "Blight", 3, spellCast,
      ));
      assert.equal(actor.state.resources["spell-slot-3"], reason === "slot" ? 0 : 1);
    } finally {
      window.IRON_PIT_BROWSER_CONDITION_RULES.canSee = priorSight;
    }
  }
  console.log("2014 universal spell interrupt standalone browser parity passed");
} catch (error) {
  console.error("2014 universal spell interrupt standalone test failed", error);
  process.exitCode = 1;
}
