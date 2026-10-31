"use strict";
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

const G = window.IRON_PIT_BROWSER_GRAPPLE;
const State = window.IRON_PIT_BROWSER_STATE;
const Attack = window.IRON_PIT_BROWSER_ATTACK;
const template = structuredClone(window.IRON_PIT_BROWSER_MONSTERS_2014["2014-giant-crab"]);
assert.ok(template, "A source-admitted 2014 grapple attack must exist.");
template.max_hp = 100;
const original = structuredClone(template);
const weapon = structuredClone(template.attacks.find(a => a.controlEffect?.grappleEscapeDc));
assert.ok(weapon);
weapon.controlEffect.grappleMaxActiveGrapples = 2;
weapon.controlEffect.restrainsWhileGrappled = true;
const member = (id, side) => ({
  combatant_id: id, side, position_ft: 5,
  state: State.buildState(structuredClone(template)),
});
const attacker = member("source", "monsters");
const targets = [0, 1, 2].map(n => member("target-" + n, "heroes"));
const setup = { heroes: targets, monsters: [attacker] };
window.IRON_PIT_DICE = {
  roll(sides) { return sides === 20 ? 19 : 1; },
  rollMany(count, sides) { return Array.from({ length: count }, () => this.roll(sides)); },
};

// Two existing successful hits occupy both universally tracked appendages.
for (const target of targets.slice(0, 2)) {
  G.apply(target.state, attacker.combatant_id, 11, 5, true);
}
assert.equal(G.sourceGrappleCount(setup, "source"), 2);
const before = targets[2].state.current_hp;
const hit = Attack.resolveAttack(1, 1, attacker, targets[2], weapon, 5, {
  setup, spendAction: false, turnKey: "1:source",
});
assert.equal(hit.hit, true);
assert.ok(targets[2].state.current_hp < before, "Ordinary weapon damage still lands.");
assert.deepEqual(targets[2].state.grapple_sources, [], "At capacity a new target is not grappled.");
assert.equal(G.sourceGrappleCount(setup, "source"), 2);

// An existing target can be released, allowing a new target immediately.
G.release(targets[0].state, "source");
assert.equal(G.sourceGrappleCount(setup, "source"), 1);
const another = Attack.resolveAttack(2, 2, attacker, targets[2], weapon, 5, {
  setup, spendAction: false, turnKey: "2:source",
});
assert.equal(another.hit, true);
assert.equal(G.sourceGrappleCount(setup, "source"), 2);
assert.deepEqual(
  targets[2].state.active_effect_ids.filter(id => id === "grappled" || id === "restrained").sort(),
  ["grappled", "restrained"],
);
targets[0].state.is_dead = true;
G.cleanup(setup);
assert.equal(G.sourceGrappleCount(setup, "source"), 2);
assert.deepEqual(template, original, "Immutable source combat template must stay unchanged.");
assert.throws(() => G.sourceGrappleCount(null, "source"), /setup/);
console.log("Universal limited-grapple source capacity browser attack regression passed.");
