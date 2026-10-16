"use strict";
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

const MONSTERS = window.IRON_PIT_BROWSER_MONSTERS_2014;
const template = MONSTERS["2014-salamander"];
assert.ok(template, "Salamander must be source-admitted");
const tail = template.attacks.find((attack) => attack.name === "Tail");
assert.ok(tail);
assert.equal(tail.grappleTargetPolicy, "auto_hit_own_grapple");
assert.deepEqual(tail.onHitDamage.map((r) => [r.diceCount, r.diceSize, r.damageType]), [[2, 6, "fire"]]);

const S = window.IRON_PIT_BROWSER_STATE;
const G = window.IRON_PIT_BROWSER_GRAPPLE;
const F = window.IRON_PIT_BROWSER_FORMATION;
const A = window.IRON_PIT_BROWSER_ATTACK;
const heroTemplate = window.IRON_PIT_BROWSER_HEROES["aurelia-brightshield-2014-l20"];
assert.ok(heroTemplate);
const member = (id, side, template, pos) => ({
  combatant_id: id, side, position_ft: pos,
  state: S.buildState(structuredClone(template)),
});
const salamander = member("salamander-instance", "monsters", template, 10);
const held = member("hero-1", "heroes", heroTemplate, 5);
const another = member("hero-2", "heroes", heroTemplate, 5);
const setup = { heroes: [held, another], monsters: [salamander], ruleset: "2014" };
G.apply(held.state, salamander.combatant_id, 14, 10, true);
assert.equal(F.targetAllowed(salamander, held, tail, setup), true);
assert.equal(F.targetAllowed(salamander, another, tail, setup), false);
assert.equal(F.automaticHit(salamander, held, tail), true);

let rolls = [];
window.IRON_PIT_DICE = {
  roll: (sides) => { rolls.push(sides); if (sides === 20) throw Error("Auto-hit rolled d20"); return 1; },
  rollMany: (count, sides) => Array.from({ length: count }, () => {
    rolls.push(sides); if (sides === 20) throw Error("Auto-hit rolled d20"); return 1;
  }),
};
S.beginTurn(salamander.state);
const before = held.state.current_hp;
const event = A.resolveAttack(1, 1, salamander, held, tail, 5, { setup });
assert.equal(event.hit, true);
assert.equal(event.critical, false);
assert.equal(event.attack_roll, null);
assert.deepEqual(event.damage_components.map((r) => r.damage_type), ["bludgeoning", "fire"]);
assert.equal(held.state.current_hp, before - 8);
assert.ok(!rolls.includes(20));
assert.equal(held.state.grapple_sources.length, 1);
G.release(held.state, salamander.combatant_id);
assert.equal(F.automaticHit(salamander, held, tail), false);
assert.equal(F.targetAllowed(salamander, another, tail, setup), true);
// Once the owner's grapple ends, ordinary attacks again require a d20 test.
let resumedD20 = 0;
window.IRON_PIT_DICE = {
  roll: (sides) => { if (sides === 20) resumedD20++; return 1; },
  rollMany: (count, sides) => Array.from({ length: count }, () => {
    if (sides === 20) resumedD20++; return 1;
  }),
};
S.beginTurn(salamander.state);
const releasedAttack = A.resolveAttack(2, 2, salamander, another, tail, 5, { setup });
assert.equal(releasedAttack.hit, false);
assert.ok(releasedAttack.attack_roll);
assert.ok(resumedD20 > 0);
assert.equal(another.state.grapple_sources.length, 0, "A missed first Tail attack never Grapples");
// Universal cleanup: truly Incapacitated grapplers release their hold.
// Mere Poisoned, Frightened, Charmed, Restrained or Grappled does not.
for (const condition of ["incapacitated", "unconscious", "stunned", "paralyzed", "petrified"]) {
  G.apply(held.state, salamander.combatant_id, 14, 10, true);
  salamander.state.active_effect_ids.push(condition);
  assert.throws(() => A.resolveAttack(10, 1, salamander, held, tail, 5,
    { setup, spendAction: false }), /incapacitated or dead/);
  G.cleanup(setup);
  assert.deepEqual(held.state.grapple_sources, [], condition);
  assert.ok(!held.state.active_effect_ids.includes("grappled"), condition);
  assert.ok(!held.state.active_effect_ids.includes("restrained"), condition);
  salamander.state.active_effect_ids.pop();
}
for (const condition of ["poisoned", "frightened", "charmed", "restrained", "grappled"]) {
  G.apply(held.state, salamander.combatant_id, 14, 10, true);
  salamander.state.active_effect_ids.push(condition);
  G.cleanup(setup);
  assert.equal(held.state.grapple_sources.length, 1, condition);
  salamander.state.active_effect_ids.pop();
  G.release(held.state, salamander.combatant_id);
}
G.apply(held.state, salamander.combatant_id, 14, 10, true);
held.state.is_unconscious = true;
held.state.current_hp = 0;
G.cleanup(setup);
assert.equal(held.state.grapple_sources.length, 1, "A living Unconscious target remains held");
held.state.is_alive = false;
held.state.is_dead = true;
held.state.is_unconscious = false;
G.cleanup(setup);
assert.equal(held.state.grapple_sources.length, 0, "Dead target releases owner hold");
assert.ok(!held.state.active_effect_ids.includes("restrained"));
// Redirect Attack must not transfer an automatic hit to an unheld target.
{
  const source = member("salamander-redirect", "monsters", template, 10);
  const boss = member("redirect-boss", "heroes", heroTemplate, 5);
  const ally = member("redirect-ally", "heroes", heroTemplate, 5);
  boss.state.template.redirect_attack_reaction = { ally_range_ft: 5, ally_max_size: "medium" };
  const encounter = { heroes: [boss, ally], monsters: [source], ruleset: "2014" };
  G.apply(boss.state, source.combatant_id, 14, 10, true);
  let d20Count = 0;
  window.IRON_PIT_DICE = {
    roll: (sides) => { if (sides === 20) d20Count++; return 1; },
    rollMany: (count, sides) => Array.from({ length: count }, () => {
      if (sides === 20) d20Count++;
      return 1;
    }),
  };
  S.beginTurn(source.state);
  const redirected = A.resolveAttack(3, 3, source, boss, tail, 5, { setup: encounter });
  assert.equal(redirected.target_id, ally.combatant_id);
  assert.equal(redirected.hit, false);
  assert.ok(redirected.attack_roll, "Unheld replacement requires a d20");
  assert.ok(d20Count > 0);
  assert.equal(boss.state.reaction_available, false);
}
console.log("Salamander shared grapple-owner auto-hit / source dice browser parity passed.");
