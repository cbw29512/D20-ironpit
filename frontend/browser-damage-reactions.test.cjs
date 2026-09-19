"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "reaction" && state.reaction_available && !state.is_dead && !state.is_unconscious,
  spend: (state, cost) => {
    if (cost !== "reaction" || !state.reaction_available) throw new Error("Reaction is unavailable.");
    state.reaction_available = false;
  },
};
window.IRON_PIT_BROWSER_FORMATION = {
  attackDistance: (a, b) => Math.abs(a.position_ft - b.position_ft),
  targetAllowed: () => true,
};

function member(id, side, position, retaliation) {
  return {
    combatant_id: id,
    side,
    position_ft: position,
    state: {
      is_alive: true,
      is_dead: false,
      is_unconscious: false,
      reaction_available: true,
      template: {
        name: id,
        attacks: [{
          id: id + "-blade",
          name: "Blade",
          kind: "melee",
          reach: 5,
        }],
        damage_triggered_reaction_attack: retaliation
          ? { source_id: "test-retaliation", max_source_distance_ft: 5, attack_kind: "melee" }
          : null,
      },
    },
  };
}

let queuedDamage = [];
window.IRON_PIT_BROWSER_ATTACK = {
  resolveAttack(sequence, round, attacker, target, attack, distance, extra) {
    assert.equal(extra.spendAction, false);
    assert.equal(extra.offTurn, true);
    const total = queuedDamage.shift() ?? 4;
    return {
      sequence,
      round_number: round,
      event_type: "attack",
      actor_id: attacker.combatant_id,
      actor_name: attacker.state.template.name,
      target_id: target.combatant_id,
      target_name: target.state.template.name,
      attack_name: attack.name,
      damage_roll: { total },
      feature_id: extra.featureId,
      animation: "slash",
      description: "Synthetic reaction attack.",
    };
  },
};

load("browser-damage-reactions.js");
const D = window.IRON_PIT_BROWSER_DAMAGE_REACTIONS;

{
  const source = member("source", "monsters", 5, false);
  const reactor = member("reactor", "heroes", 0, true);
  const setup = { heroes: [reactor], monsters: [source] };
  const trigger = {
    event_type: "attack", actor_id: "source", target_id: "reactor",
    damage_roll: { total: 4 },
  };
  queuedDamage = [4];
  const result = D.resolveAfterDamage(2, 1, source, trigger, setup, "1:source");
  assert.equal(result.sequence, 3);
  assert.equal(result.events.length, 1);
  assert.equal(result.events[0].feature_id, "test-retaliation");
  assert.equal(reactor.state.reaction_available, false);
}

{
  const source = member("source", "monsters", 5, true);
  const reactor = member("reactor", "heroes", 0, true);
  const setup = { heroes: [reactor], monsters: [source] };
  const trigger = {
    event_type: "attack", actor_id: "source", target_id: "reactor",
    damage_roll: { total: 4 },
  };
  queuedDamage = [4, 4];
  const result = D.resolveAfterDamage(2, 1, source, trigger, setup, "1:source");
  assert.equal(result.sequence, 4);
  assert.deepEqual(result.events.map((event) => event.actor_id), ["reactor", "source"]);
  assert.equal(reactor.state.reaction_available, false);
  assert.equal(source.state.reaction_available, false);
}

{
  const source = member("source", "monsters", 10, false);
  const reactor = member("reactor", "heroes", 0, true);
  const setup = { heroes: [reactor], monsters: [source] };
  const trigger = {
    event_type: "attack", actor_id: "source", target_id: "reactor",
    damage_roll: { total: 4 },
  };
  assert.deepEqual(D.resolveAfterDamage(2, 1, source, trigger, setup), { events: [], sequence: 2 });
  trigger.damage_roll.total = 0;
  source.position_ft = 5;
  assert.deepEqual(D.resolveAfterDamage(2, 1, source, trigger, setup), { events: [], sequence: 2 });
}

console.log("Browser post-damage reaction dispatch passed.");
