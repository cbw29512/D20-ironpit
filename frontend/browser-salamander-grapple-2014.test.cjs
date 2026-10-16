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
console.log("Salamander shared grapple-owner auto-hit / source dice browser parity passed.");
