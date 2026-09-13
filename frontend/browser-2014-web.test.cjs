"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

window.IRON_PIT_BROWSER_CONDITION_RULES = { incapacitated: () => false };
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_TIMED = { strengthD20Disadvantage: () => 0 };
window.IRON_PIT_BROWSER_TACTICAL_MIND = null;
window.IRON_PIT_BROWSER_GRAPPLE = { cleanup: () => {}, shouldEscape: () => false, escape: () => null };

load("browser-action-economy.js");
load("browser-rolls.js");
load("browser-restraints.js");

let hit = true;
window.IRON_PIT_BROWSER_ATTACK = {
  resolveAttack: (sequence, round, member, target, attack) => ({
    sequence, round_number: round, event_type: "attack", actor_id: member.combatant_id,
    actor_name: member.state.template.name, target_id: target.combatant_id,
    target_name: target.state.template.name, attack_name: attack.name, hit,
    applied_condition_ids: [], description: `${attack.name}: ${hit ? "HIT" : "MISS"}.`,
  }),
};
load("browser-attack-resources.js");

const web = {
  id: "web", name: "Web", kind: "ranged", diceCount: 0, diceSize: 6, damageBonus: 0,
  normal: 30, long: 60, resourceId: "web", resourceCost: 1,
  breakableRestraint: {
    conditionId: "restrained", escapeAbility: "strength", escapeDc: 12,
    objectAc: 10, objectHp: 5, damageVulnerabilities: ["fire"],
    damageImmunities: ["bludgeoning", "poison", "psychic"],
  },
};
function actor() {
  return {
    combatant_id: "monster:spider", side: "monsters",
    state: {
      resources: { web: 1 }, action_available: true, bonus_action_available: true, reaction_available: true,
      is_dead: false, is_unconscious: false, turn_terminated: false, active_effect_ids: [], restraint_sources: [],
      template: {
        name: "Giant Spider", attacks: [web], ability_modifiers: { strength: 2 },
        resource_definitions: [{ id: "web", name: "Web", maxUses: 1, recharge: { trigger: "start_of_turn", dieSize: 6, minimumRoll: 5 } }],
      },
    },
  };
}
function target() {
  return {
    combatant_id: "hero:target", side: "heroes",
    state: {
      action_available: true, bonus_action_available: true, reaction_available: true,
      is_dead: false, is_unconscious: false, turn_terminated: false, active_effect_ids: [], restraint_sources: [], grapple_sources: [], timed_effects: [],
      template: { name: "Target", ability_modifiers: { strength: 3 } },
    },
  };
}
const dice = (values) => {
  const queue = [...values];
  window.IRON_PIT_DICE = { roll: () => queue.shift(), rollMany: (count) => Array.from({ length: count }, () => queue.shift()) };
};

{
  const spider = actor(), victim = target(); hit = true;
  const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(1, 1, spider, victim, web, 30, { setup: { heroes: [victim], monsters: [spider] } });
  assert.equal(spider.state.resources.web, 0);
  assert.equal(event.resource_remaining, 0);
  assert.deepEqual(event.applied_condition_ids, ["restrained"]);
  assert.equal(victim.state.restraint_sources.length, 1);
  assert(victim.state.active_effect_ids.includes("restrained"));

  dice([20]);
  const escaped = window.IRON_PIT_BROWSER_RESTRAINTS.escape(2, 1, victim);
  assert.equal(escaped.check_succeeded, true);
  assert.equal(victim.state.action_available, false);
  assert.equal(victim.state.restraint_sources.length, 0);
  assert(!victim.state.active_effect_ids.includes("restrained"));

  dice([5]);
  const recharge = window.IRON_PIT_ACTION_ECONOMY.startTurnRecharges(3, 2, spider);
  assert.equal(recharge.events[0].resource_remaining, 1);
  assert.equal(spider.state.resources.web, 1);
}
{
  const spider = actor(), victim = target(); hit = false;
  const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(1, 1, spider, victim, web, 30, { setup: { heroes: [victim], monsters: [spider] } });
  assert.equal(event.hit, false);
  assert.equal(spider.state.resources.web, 0);
  assert.equal(victim.state.restraint_sources.length, 0);
  assert.throws(() => window.IRON_PIT_BROWSER_ATTACK.resolveAttack(2, 1, spider, victim, web, 30), /resource is unavailable/);
}

console.log("2014 browser Web Recharge/restraint regressions passed.");
