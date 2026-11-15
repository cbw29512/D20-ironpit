"use strict";
// A renamed synthetic control uses the same hit, Grapple, and object lifecycle.
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

try {
  const State = window.IRON_PIT_BROWSER_STATE;
  const Attack = window.IRON_PIT_BROWSER_ATTACK;
  const Breakable = window.IRON_PIT_BROWSER_BREAKABLE_CONDITION_OBJECT;
  const Grapple = window.IRON_PIT_BROWSER_GRAPPLE;
  const template = structuredClone(window.IRON_PIT_BROWSER_MONSTERS_2014["2014-giant-crab"]);
  assert.ok(template, "A source-admitted grapple template is required.");
  const sourceCopy = structuredClone(template);
  const attack = structuredClone(template.attacks.find((item) =>
    item.controlEffect?.grappleEscapeDc));
  assert.ok(attack);
  attack.id = "renamed-generic-snare";
  attack.name = "Renamed Generic Snare";
  attack.diceCount = 0;
  attack.damageBonus = 0;
  attack.fixedDamage = 0;
  attack.controlEffect.grappleEscapeDc = 15;
  attack.controlEffect.restrainsWhileGrappled = true;
  attack.controlEffect.grappleMaxActiveGrapples = 6;
  attack.controlEffect.grappleBreakableObject = {
    armorClass: 20, hitPoints: 10,
    damageVulnerabilities: [], damageImmunities: ["poison", "psychic"],
  };
  const member = (id, side) => ({
    combatant_id: id, side, position_ft: 5,
    state: State.buildState(structuredClone(template)),
  });
  const source = member("owner", "monsters");
  const victim = member("victim", "heroes");
  const setup = {heroes: [victim], monsters: [source]};
  const sourceHp = source.state.current_hp;
  const victimHp = victim.state.current_hp;
  window.IRON_PIT_DICE = {
    roll: (sides) => sides === 20 ? 19 : 1,
    rollMany: (count, sides) => Array.from({length: count}, () => sides === 20 ? 19 : 1),
  };

  const result = Attack.resolveAttack(1, 1, source, victim, attack, 5, {
    setup, spendAction: false, turnKey: "1:owner",
  });
  assert.equal(result.hit, true);
  assert.equal(victim.state.grapple_sources.length, 1);
  const grapple = victim.state.grapple_sources[0];
  assert.equal(grapple.breakable_object.armor_class, 20);
  assert.equal(grapple.breakable_object.current_hp, 10);
  assert.deepEqual(grapple.breakable_object.damage_immunities, ["poison", "psychic"]);
  assert.equal(Grapple.sourceGrappleCount(setup, "owner"), 1);

  assert.deepEqual(Breakable.damageGrapple(victim.state, grapple, 19, 5, "slashing", setup),
    {appliedDamage: 0, destroyed: false});
  assert.deepEqual(Breakable.damageGrapple(victim.state, grapple, 20, 99, "poison", setup),
    {appliedDamage: 0, destroyed: false});
  assert.deepEqual(Breakable.damageGrapple(victim.state, grapple, 20, 99, "psychic", setup),
    {appliedDamage: 0, destroyed: false});
  assert.deepEqual(Breakable.damageGrapple(victim.state, grapple, 20, 4, "slashing", setup),
    {appliedDamage: 4, destroyed: false});
  assert.equal(grapple.breakable_object.current_hp, 6);
  assert.deepEqual(Breakable.damageGrapple(victim.state, grapple, 20, 6, "piercing", setup),
    {appliedDamage: 6, destroyed: true});
  assert.deepEqual(victim.state.grapple_sources, []);
  assert.equal(Grapple.sourceGrappleCount(setup, "owner"), 0);
  assert.equal(Grapple.sourceGrappleCapacityUsed(setup, "owner", attack.id), 1);
  // Five intact tendrils plus one broken use every printed capacity slot.
  const held = Array.from({length: 5}, (_, n) => member("held-" + n, "heroes"));
  setup.heroes.push(...held);
  for (const target of held) {
    Attack.resolveAttack(2, 1, source, target, attack, 5, {
      setup, spendAction: false, turnKey: "1:owner",
    });
    assert.equal(target.state.grapple_sources.length, 1);
  }
  assert.equal(Grapple.sourceGrappleCapacityUsed(setup, "owner", attack.id), 6);
  const sixth = member("sixth", "heroes");
  setup.heroes.push(sixth);
  Attack.resolveAttack(3, 1, source, sixth, attack, 5, {
    setup, spendAction: false, turnKey: "1:owner",
  });
  assert.deepEqual(sixth.state.grapple_sources, [],
    "Broken slot prevents immediate sixth replacement.");
  State.beginTurn(source.state);
  assert.equal(Grapple.sourceGrappleCapacityUsed(setup, "owner", attack.id), 5);
  Attack.resolveAttack(4, 2, source, sixth, attack, 5, {
    setup, spendAction: false, turnKey: "2:owner",
  });
  assert.equal(sixth.state.grapple_sources.length, 1,
    "The source may extrude the sixth tendril on its next turn.");

  assert.ok(!victim.state.active_effect_ids.includes("grappled"));
  assert.ok(!victim.state.active_effect_ids.includes("restrained"));
  assert.equal(source.state.current_hp, sourceHp, "Destroying an appendage cannot damage its owner.");
  assert.equal(victim.state.current_hp, victimHp, "Attack and object damage must not hit the held creature.");
  assert.deepEqual(template, sourceCopy, "The immutable card cannot lose object HP.");
  assert.throws(() => Breakable.damageGrapple(victim.state, grapple, 20, 10, "slashing", setup),
    /no active breakable Grapple object/);
} catch (error) {
  console.error("Universal source-owned breakable Grapple regression failed.", error);
  throw error;
}
console.log("Generic breakable Grapple browser parity passed.");
