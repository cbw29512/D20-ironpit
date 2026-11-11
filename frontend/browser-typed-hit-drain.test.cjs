"use strict";

// Exercise the real shared browser healing and maximum-HP primitives.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
window.IRON_PIT_BROWSER_STATE = {
  effectiveMaxHp(state) {
    return Math.max(1, state.template.max_hp + (state.max_hp_bonus || 0)
      - (state.hit_point_maximum_reduction || 0));
  },
};
window.IRON_PIT_BROWSER_HEALING_POLICY = { swarm: () => false };
window.IRON_PIT_BROWSER_CONDITION_RULES = {
  incapacitated: (state) => Boolean(state.is_unconscious
    || (state.active_effect_ids || []).includes("incapacitated")),
};
load("browser-healing.js");
load("browser-maximum-hp.js");
load("browser-formation.js");

function member(id, hp = 30) {
  return {
    combatant_id: id, side: "monsters",
    state: {
      template: { id: "synthetic-" + id, name: id, max_hp: hp, kind: "monster" },
      current_hp: hp, temporary_hp: 0, max_hp_bonus: 0, hit_point_maximum_reduction: 0,
      active_effect_ids: [], grapple_sources: [], willing_attack_source_ids: [],
      timed_effects: [], is_alive: true, is_dead: false, is_unconscious: false,
      is_stable: false, death_save_successes: 0, death_save_failures: 0,
    },
  };
}
const drainingAttack = {
  id: "renamed-source", name: "Renamed Attack", kind: "melee",
  targetQualification: {
    anyOf: ["source_grappled", "incapacitated", "restrained", "willing"],
  },
  onHitTypedDrain: {
    damageType: "necrotic", reduceTargetMaximumHp: true,
    healAttacker: true, zeroMaximumHpKills: true,
  },
};
const targetAllowed = window.IRON_PIT_BROWSER_FORMATION.targetAllowed;
{
  const actor = member("drainer"), victim = member("victim");
  assert.equal(targetAllowed(actor, victim, drainingAttack), false);
  victim.state.active_effect_ids.push("restrained");
  assert.equal(targetAllowed(actor, victim, drainingAttack), true);
  victim.state.active_effect_ids.length = 0;
  victim.state.willing_attack_source_ids.push(actor.combatant_id);
  assert.equal(targetAllowed(actor, victim, drainingAttack), true);
  victim.state.willing_attack_source_ids.length = 0;
  victim.state.grapple_sources.push({ source_id: actor.combatant_id });
  assert.equal(targetAllowed(actor, victim, drainingAttack), true);
  victim.state.grapple_sources.length = 0;
  victim.state.active_effect_ids.push("incapacitated");
  assert.equal(targetAllowed(actor, victim, drainingAttack), true);
}
{
  const actor = member("renamed-monster", 40), victim = member("target", 30);
  actor.state.current_hp = 17;
  const result = window.IRON_PIT_BROWSER_MAXIMUM_HP.resolveTypedDrain(
    actor, victim, drainingAttack, [
      { damageType: "piercing", appliedTotal: 8 },
      { damageType: "necrotic", appliedTotal: 5 },
    ],
  );
  assert.deepEqual(result, {
    damageTaken: 5, maximumReduced: 5, healed: 5, killedByZeroMaximum: false,
  });
  assert.equal(actor.state.current_hp, 22);
  assert.equal(victim.state.hit_point_maximum_reduction, 5);
  assert.equal(victim.state.template.max_hp, 30);
  const immune = window.IRON_PIT_BROWSER_MAXIMUM_HP.resolveTypedDrain(
    actor, victim, drainingAttack, [
      { damageType: "piercing", appliedTotal: 9 },
      { damageType: "necrotic", appliedTotal: 0 },
    ],
  );
  assert.equal(immune.damageTaken, 0);
  assert.equal(actor.state.current_hp, 22);
  assert.equal(victim.state.hit_point_maximum_reduction, 5);
}
{
  // Damage can destroy maximum HP even if normal HP was protected by temp HP.
  const actor = member("actor", 20), victim = member("victim", 3);
  actor.state.current_hp = 9;
  victim.state.temporary_hp = 100;
  const result = window.IRON_PIT_BROWSER_MAXIMUM_HP.resolveTypedDrain(
    actor, victim, drainingAttack, [{ damageType: "necrotic", appliedTotal: 5 }],
  );
  assert.equal(result.killedByZeroMaximum, true);
  assert.equal(victim.state.is_dead, true);
  assert.equal(actor.state.current_hp, 14);
  assert.equal(victim.state.template.max_hp, 3);
}
console.log("Browser typed damage-drain and strict target-eligibility regressions passed.");
