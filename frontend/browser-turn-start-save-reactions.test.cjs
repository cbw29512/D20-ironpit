"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const test = require("node:test");

global.window = globalThis;
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-turn-start-save-reactions.js"), "utf8"),
  { filename: "browser-turn-start-save-reactions.js" },
);
const R = window.IRON_PIT_BROWSER_TURN_START_SAVE_REACTIONS;

function setupEncounter() {
  const rule = {
    source_id: "turn-start-fear", source_name: "Turn-start Fear",
    trigger: "other_creature_turn_start", range_ft: 30,
    source_must_see_target: true, target_must_see_source: true,
    save_ability: "wisdom", save_dc: 14,
    failure_condition: "frightened", expires_at: "target_turn_end",
  };
  const source = {
    combatant_id: "source", side: "monsters", position_ft: 0,
    state: { is_alive: true, is_dead: false, current_hp: 20,
      reaction_available: true, template: { name: "Reaction Source", turn_start_save_reaction: rule } },
  };
  const target = {
    combatant_id: "target", side: "heroes", position_ft: 30,
    state: { is_alive: true, is_dead: false, current_hp: 20, template: { name: "Target" } },
  };
  const setup = { heroes: [target], monsters: [source] };
  const seen = [];
  window.IRON_PIT_BROWSER_STATE = {
    distance: (a, b) => Math.abs(a.position_ft - b.position_ft),
  };
  window.IRON_PIT_BROWSER_CONDITION_RULES = {
    canSee: (a, b, distance) => { seen.push([a, b, distance]); return true; },
  };
  window.IRON_PIT_ACTION_ECONOMY = {
    available: (state, cost) => cost === "reaction" && state.reaction_available,
    spend: (state, cost) => { assert.equal(cost, "reaction"); state.reaction_available = false; },
  };
  window.IRON_PIT_BROWSER_SAVES = {
    resolveSavingThrow: (_state, ability, dc, context) => {
      assert.equal(ability, "wisdom"); assert.equal(dc, 14);
      assert.equal(context.conditionId, "frightened");
      return { roll: { total: 9 }, succeeded: false };
    },
  };
  window.IRON_PIT_BROWSER_TIMED = {
    apply: (state, condition, owner, options) => {
      seen.push([state, condition, owner, options]);
      return condition;
    },
  };
  return { source, target, setup, seen };
}

test("two-way visibility and range gate turn-start Reactions", () => {
  const { source, target, seen } = setupEncounter();
  assert.equal(R.eligible(source, target), true);
  assert.deepEqual(seen.map((item) => item[2]), [30, 30]);
  window.IRON_PIT_BROWSER_CONDITION_RULES.canSee = (a) => a === source.state;
  assert.equal(R.eligible(source, target), false);
  target.position_ft = 35;
  assert.equal(R.eligible(source, target), false);
  target.position_ft = 5;
  source.state.reaction_available = false;
  assert.equal(R.eligible(source, target), false);
  assert.equal(R.eligible(source, { ...target, side: "monsters" }), false);
});

test("failed save spends one Reaction and expires Frightened at target turn end", () => {
  const { source, target, setup, seen } = setupEncounter();
  const result = R.resolve(7, 2, target, setup);
  assert.equal(result.sequence, 8);
  assert.equal(result.events.length, 1);
  assert.equal(result.events[0].feature_id, "turn-start-fear");
  assert.equal(result.events[0].save_succeeded, false);
  assert.deepEqual(result.events[0].applied_condition_ids, ["frightened"]);
  assert.equal(source.state.reaction_available, false);
  const application = seen.find((row) => row[1] === "frightened");
  assert.equal(application[2], "source");
  assert.equal(application[3].expiryTiming, "target_turn_end");
  assert.equal(application[3].sourceEffectId, "turn-start-fear");
  assert.deepEqual(R.resolve(8, 2, target, setup).events, []);
});

test("successful save spends Reaction without creating a debuff", () => {
  const { source, target, setup, seen } = setupEncounter();
  window.IRON_PIT_BROWSER_SAVES.resolveSavingThrow = () => ({
    roll: { total: 19 }, succeeded: true,
  });
  const result = R.resolve(1, 1, target, setup);
  assert.equal(result.events[0].save_succeeded, true);
  assert.deepEqual(result.events[0].applied_condition_ids, []);
  assert.equal(source.state.reaction_available, false);
  assert.equal(seen.some((row) => row[1] === "frightened"), false);
});

test("missing source rule does not consume a Reaction", () => {
  const { source, target, setup } = setupEncounter();
  source.state.template.turn_start_save_reaction = null;
  assert.deepEqual(R.resolve(3, 1, target, setup), { events: [], sequence: 3 });
  assert.equal(source.state.reaction_available, true);
});
