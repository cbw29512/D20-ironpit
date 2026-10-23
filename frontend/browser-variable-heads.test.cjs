const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

function load(path) {
  vm.runInThisContext(fs.readFileSync(path, "utf8"), { filename: path });
}

test("browser variable heads mirror sever, fire, regrowth, and OA budgets", () => {
  global.window = {};
  load("frontend/browser-variable-heads.js");
  window.IRON_PIT_BROWSER_STATE = { effectiveMaxHp: () => 172 };
  const state = {
    template: { variableHeads: {
      initialHeads: 5, severDamageThreshold: 25, headsPerRegrowth: 2,
      healingPerRegrownHead: 10, regrowthBlockingDamageTypes: ["fire"],
      extraOpportunityReactionsPerHeadBeyondOne: true,
    }},
    current_hp: 100, is_dead: false, reaction_available: true,
    timed_effects: [], damage_taken_this_turn_by_type: {},
  };
  const H = window.IRON_PIT_BROWSER_VARIABLE_HEADS;
  H.initialize(state);
  assert.equal(state.current_heads, 5);
  state.damage_taken_this_turn_by_type = { slashing: 25 };
  assert.equal(H.noteDamage(state, {}), false);
  assert.equal(state.current_heads, 4);
  state.damage_taken_this_turn_by_type = { slashing: 125 };
  H.noteDamage(state, { slashing: 25 });
  assert.equal(state.current_heads, 4);
  state.damage_taken_this_turn_by_type = { fire: 25 };
  H.noteDamage(state, {});
  assert.deepEqual(H.endOwnerTurn(state), { grown: 0, healed: 0 });

  state.damage_taken_this_turn_by_type = { slashing: 25 };
  H.noteDamage(state, {});
  state.damage_taken_this_turn_by_type = {};
  assert.deepEqual(H.endOwnerTurn(state), { grown: 2, healed: 20 });
  H.refreshOpportunityReactions(state);
  H.spendOpportunityReaction(state);
  assert.equal(state.reaction_available, false);
  H.spendOpportunityReaction(state);
  assert.equal(state.opportunity_reactions_remaining, state.current_heads - 2);
});

test("browser Multiattack expands from current mutable head count", () => {
  global.window = {
    IRON_PIT_BROWSER_FORMATION: {},
    IRON_PIT_BROWSER_SAVES: {},
    IRON_PIT_ACTION_ECONOMY: {},
  };
  load("frontend/browser-multiattack-choices.js");
  const slot = { attackIds: ["bite"], saveActionIds: [] };
  const member = { state: {
    current_heads: 3,
    template: { attack_action: { repeatCountFromVariableHeads: true } },
  }};
  const result = window.IRON_PIT_BROWSER_MULTIATTACK_CHOICES.expandedSlots(
    { id: "heads", slots: [slot] }, member,
  );
  assert.equal(result.slots.length, 3);
  assert.equal(result.repetitionRoll, null);
});
