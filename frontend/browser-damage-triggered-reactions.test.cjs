"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "reaction"
    && state.reaction_available && !state.is_dead && !state.is_unconscious,
  spend: (state, cost) => {
    if (cost !== "reaction" || !state.reaction_available) throw new Error("Reaction unavailable.");
    state.reaction_available = false;
  },
};
window.IRON_PIT_BROWSER_STATE = {
  distance: (left, right) => Math.abs(left.position_ft - right.position_ft),
};
let lastAttackExtra = null;
window.IRON_PIT_BROWSER_ATTACK = {
  resolveAttack: (sequence, round, actor, target, attack, _distance, extra) => {
    lastAttackExtra = extra;
    const before = target.state.current_hp;
    target.state.current_hp = Math.max(0, before - 1);
    return {
      sequence,
      round_number: round,
      event_type: "attack",
      actor_id: actor.combatant_id,
      actor_name: actor.state.template.name,
      target_id: target.combatant_id,
      target_name: target.state.template.name,
      weapon_id: attack.id,
      feature_id: extra.featureId,
      hp_before: before,
      hp_after: target.state.current_hp,
      temporary_hp_before: 0,
      temporary_hp_after: 0,
      damage_roll: { total: 1 },
      damage_components: [{ applied_total: 1 }],
    };
  },
};

load("browser-damage-triggered-reactions.js");
load("browser-damage-reaction-dispatch.js");

const melee = { id: "greataxe", kind: "melee", reach: 5 };
function member(id, side, position, reaction = false) {
  return {
    combatant_id: id,
    side,
    position_ft: position,
    state: {
      current_hp: 20,
      is_alive: true,
      is_dead: false,
      is_unconscious: false,
      action_available: true,
      reaction_available: true,
      grapple_sources: [],
      template: {
        name: id,
        attacks: [melee],
        damage_triggered_melee_reaction: reaction
          ? { id: "retaliation", trigger_range_ft: 5 }
          : null,
      },
    },
  };
}
function damageEvent(source, target, applied = 2) {
  return {
    sequence: 1,
    actor_id: source.combatant_id,
    target_id: target.combatant_id,
    hp_before: target.state.current_hp + applied,
    hp_after: target.state.current_hp,
    temporary_hp_before: 0,
    temporary_hp_after: 0,
    damage_roll: { total: applied },
    damage_components: [{ applied_total: applied }],
  };
}

{
  const reactor = member("reactor", "heroes", 0, true);
  const source = member("source", "monsters", 5, false);
  const setup = { heroes: [reactor], monsters: [source] };
  const result = window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH.resolve(
    2, 1, source, damageEvent(source, reactor), setup, "1:source",
  );
  assert.equal(result.events.length, 1);
  assert.equal(result.events[0].feature_id, "retaliation");
  assert.equal(result.events[0].actor_id, "reactor");
  assert.equal(result.events[0].target_id, "source");
  assert.equal(reactor.state.reaction_available, false);
  assert.equal(reactor.state.action_available, true);
  assert.equal(lastAttackExtra.spendAction, false);
  assert.equal(lastAttackExtra.offTurn, true);
  assert.equal(lastAttackExtra.allowReckless, false);
  assert.equal(result.sequence, 3);
}

{
  const reactor = member("far-reactor", "heroes", 0, true);
  const source = member("far-source", "monsters", 10, false);
  const setup = { heroes: [reactor], monsters: [source] };
  const result = window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH.resolve(
    2, 1, source, damageEvent(source, reactor), setup,
  );
  assert.deepEqual(result.events, []);
  assert.equal(reactor.state.reaction_available, true);
}

{
  const reactor = member("zero-reactor", "heroes", 0, true);
  const source = member("zero-source", "monsters", 5, false);
  const setup = { heroes: [reactor], monsters: [source] };
  const event = damageEvent(source, reactor, 0);
  event.damage_roll.total = 10;
  event.damage_components = [{ applied_total: 0 }];
  const result = window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH.resolve(
    2, 1, source, event, setup,
  );
  assert.deepEqual(result.events, []);
  assert.equal(reactor.state.reaction_available, true);
}

{
  const reactor = member("sleeping-reactor", "heroes", 0, true);
  reactor.state.is_unconscious = true;
  const source = member("sleep-source", "monsters", 5, false);
  const setup = { heroes: [reactor], monsters: [source] };
  const result = window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH.resolve(
    2, 1, source, damageEvent(source, reactor), setup,
  );
  assert.deepEqual(result.events, []);
  assert.equal(reactor.state.reaction_available, true);
}

{
  const left = member("left", "heroes", 0, true);
  const right = member("right", "monsters", 5, true);
  const setup = { heroes: [left], monsters: [right] };
  const result = window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH.resolve(
    2, 1, right, damageEvent(right, left), setup,
  );
  assert.deepEqual(result.events.map((event) => event.feature_id), ["retaliation", "retaliation"]);
  assert.equal(left.state.reaction_available, false);
  assert.equal(right.state.reaction_available, false);
  assert.equal(result.sequence, 4);
}

console.log("Browser universal post-damage reaction regressions passed.");
