"use strict";

const fs = require("node:fs");
const vm = require("node:vm");
const assert = require("node:assert/strict");
global.window = globalThis;

function load(file) {
  vm.runInThisContext(fs.readFileSync(require("node:path").join(__dirname, file), "utf8"), { filename: file });
}

window.IRON_PIT_BROWSER_EXHAUSTION = {
  gain(state, levels = 1) { state.exhaustion_level = Math.min(6, (state.exhaustion_level || 0) + levels); return state.exhaustion_level; },
  reduce(state, levels = 1) { state.exhaustion_level = Math.max(0, (state.exhaustion_level || 0) - levels); return state.exhaustion_level; },
};
window.IRON_PIT_BROWSER_STATE = {
  nearestTarget: (_member, setup) => setup.heroes[0],
  distance: () => 5,
};
const attackCalls = [];
window.IRON_PIT_BROWSER_ATTACK = {
  resolveAttack(sequence, round, member, target, attack) {
    attackCalls.push(attack.id);
    return {
      sequence, round_number: round, event_type: "attack",
      actor_id: member.combatant_id, actor_name: member.state.template.name,
      target_id: target.combatant_id, target_name: target.state.template.name,
      attack_id: attack.id, attack_name: attack.name, feature_id: null,
      animation: "strike", description: "attached attack",
    };
  },
};
load("browser-triggered-extra-attacks.js");

const rule = {
  sourceId: "loathsome-limbs",
  sourceName: "Loathsome Limbs",
  triggerDamageType: "slashing",
  triggerDamageMinimum: 15,
  requiresBloodied: true,
  maxStacks: 4,
  maxUses: 4,
  exhaustionPerStack: 1,
  clearsOnRegenerationHeal: true,
  attack: { id: "attached-limb-rend", name: "Rend", kind: "melee", bonus: 6, diceCount: 2, diceSize: 4, damageBonus: 4, damageType: "slashing", reach: 5 },
};

function member() {
  return {
    combatant_id: "monster-1:troll", side: "monsters", position_ft: 5,
    state: {
      template: { name: "Troll", max_hp: 94, triggered_extra_attack_stacks: [rule] },
      current_hp: 40, is_dead: false, exhaustion_level: 0,
      damage_taken_this_turn_by_type: {}, feature_use_counts: {},
      triggered_extra_attack_stack_counts: {}, source_owned_exhaustion_levels: {},
    },
  };
}
const hero = { combatant_id: "hero-1", side: "heroes", position_ft: 0, state: { template: { name: "Hero" }, current_hp: 100, is_dead: false } };
const setup = { heroes: [hero], monsters: [] };

{
  const troll = member();
  setup.monsters = [troll];
  troll.state.current_hp = 60;
  troll.state.damage_taken_this_turn_by_type.slashing = 15;
  let result = window.IRON_PIT_BROWSER_TRIGGERED_EXTRA_ATTACKS.resolveAfterTurn(1, 1, troll, setup);
  assert.equal(result.events.length, 0);

  troll.state.current_hp = 40;
  troll.state.damage_taken_this_turn_by_type.slashing = 14;
  result = window.IRON_PIT_BROWSER_TRIGGERED_EXTRA_ATTACKS.resolveAfterTurn(1, 1, troll, setup);
  assert.equal(result.events.length, 0);

  troll.state.damage_taken_this_turn_by_type.slashing = 15;
  attackCalls.length = 0;
  result = window.IRON_PIT_BROWSER_TRIGGERED_EXTRA_ATTACKS.resolveAfterTurn(1, 1, troll, setup);
  assert.deepEqual(result.events.map((event) => event.event_type), ["feature", "attack"]);
  assert.equal(troll.state.triggered_extra_attack_stack_counts["loathsome-limbs"], 1);
  assert.equal(troll.state.feature_use_counts["loathsome-limbs"], 1);
  assert.equal(troll.state.exhaustion_level, 1);
  assert.deepEqual(attackCalls, ["attached-limb-rend"]);
}

{
  const troll = member();
  setup.monsters = [troll];
  for (let expected = 1; expected <= 4; expected += 1) {
    troll.state.damage_taken_this_turn_by_type.slashing = 20;
    attackCalls.length = 0;
    window.IRON_PIT_BROWSER_TRIGGERED_EXTRA_ATTACKS.resolveAfterTurn(1, expected, troll, setup);
    assert.equal(troll.state.triggered_extra_attack_stack_counts["loathsome-limbs"], expected);
    assert.equal(troll.state.exhaustion_level, expected);
    assert.equal(attackCalls.length, expected);
  }
  attackCalls.length = 0;
  window.IRON_PIT_BROWSER_TRIGGERED_EXTRA_ATTACKS.resolveAfterTurn(1, 5, troll, setup);
  assert.equal(troll.state.triggered_extra_attack_stack_counts["loathsome-limbs"], 4);
  assert.equal(troll.state.feature_use_counts["loathsome-limbs"], 4);
  assert.equal(troll.state.exhaustion_level, 4);
  assert.equal(attackCalls.length, 4);
}

{
  // End-any-turn stack timing: another creature ends its turn after damaging the Troll.
  const troll = member();
  setup.monsters = [troll];
  troll.state.current_hp = 40;
  troll.state.damage_taken_this_turn_by_type.slashing = 15;
  attackCalls.length = 0;
  let result = window.IRON_PIT_BROWSER_TRIGGERED_EXTRA_ATTACKS.resolveAfterTurn(1, 1, hero, setup);
  assert.deepEqual(result.events.map((event) => event.event_type), ["feature"]);
  assert.equal(troll.state.triggered_extra_attack_stack_counts["loathsome-limbs"], 1);
  assert.equal(attackCalls.length, 0);

  window.IRON_PIT_BROWSER_TRIGGERED_EXTRA_ATTACKS.clearTurnDamage(setup);
  assert.deepEqual(troll.state.damage_taken_this_turn_by_type, {});
  assert.deepEqual(hero.state.damage_taken_this_turn_by_type, {});

  attackCalls.length = 0;
  result = window.IRON_PIT_BROWSER_TRIGGERED_EXTRA_ATTACKS.resolveAfterTurn(result.sequence, 1, troll, setup);
  assert.deepEqual(result.events.map((event) => event.event_type), ["attack"]);
  assert.equal(troll.state.triggered_extra_attack_stack_counts["loathsome-limbs"], 1);
  assert.deepEqual(attackCalls, ["attached-limb-rend"]);
}

{
  const troll = member();
  setup.monsters = [troll];
  troll.state.triggered_extra_attack_stack_counts["loathsome-limbs"] = 2;
  troll.state.source_owned_exhaustion_levels["loathsome-limbs"] = 2;
  troll.state.exhaustion_level = 3;
  const cleared = window.IRON_PIT_BROWSER_TRIGGERED_EXTRA_ATTACKS.clearRegenerationOwnedStacks(troll.state);
  assert.deepEqual(cleared, [{ sourceName: "Loathsome Limbs", stacks: 2 }]);
  assert.equal(troll.state.exhaustion_level, 1);
  assert.equal(troll.state.triggered_extra_attack_stack_counts["loathsome-limbs"], undefined);
}

console.log("Browser triggered extra-attack stack parity passed.");
