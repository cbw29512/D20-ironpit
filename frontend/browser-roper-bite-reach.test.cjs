"use strict";
// Generic control-and-melee sequencing; Roper only supplies source parameters.
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

try {
  const base = structuredClone(window.IRON_PIT_BROWSER_MONSTERS_2014["2014-giant-crab"]);
  assert.ok(base, "Expected a source-admitted generic Grapple combatant.");
  const tendril = structuredClone(base.attacks.find(a => a.controlEffect?.grappleEscapeDc));
  assert.ok(tendril);
  tendril.id = "renamed-control-reach";
  tendril.name = "Renamed Control";
  tendril.kind = "melee";
  tendril.reach = 50;
  tendril.diceCount = 0;
  tendril.damageBonus = 0;
  tendril.fixedDamage = 0;
  tendril.controlEffect.grappleEscapeDc = 15;
  tendril.controlEffect.restrainsWhileGrappled = true;
  tendril.controlEffect.grappleMaxActiveGrapples = 6;
  tendril.controlEffect.grappleBreakableObject = {
    armorClass: 20, hitPoints: 10,
    damageVulnerabilities: [], damageImmunities: ["poison", "psychic"],
  };
  const bite = structuredClone(tendril);
  bite.id = "renamed-followup-bite";
  bite.name = "Renamed Bite";
  bite.reach = 5;
  bite.controlEffect = null;
  bite.fixedDamage = 4;
  base.attacks.push(tendril, bite);

  const state = window.IRON_PIT_BROWSER_STATE;
  const formation = window.IRON_PIT_BROWSER_FORMATION;
  const engine = window.IRON_PIT_BROWSER_ATTACK;
  const make = (id, side, position_ft) => ({
    combatant_id: id, side, position_ft,
    state: state.buildState(structuredClone(base)),
  });
  const owner = make("owner", "monsters", 0);
  const victim = make("victim", "heroes", 40);
  const setup = {heroes: [victim], monsters: [owner]};
  assert.equal(formation.chooseSlotAttack(owner, setup, [tendril.id]).attack.id, tendril.id);
  assert.equal(formation.chooseSlotAttack(owner, setup, [bite.id]), null,
    "Long-reach control cannot make the short-reach Bite legal.");

  const savedDice = window.IRON_PIT_DICE;
  try {
    window.IRON_PIT_DICE = {
      roll: sides => sides === 20 ? 18 : 1,
      rollMany: (count, sides) => Array.from({length: count}, () => sides === 20 ? 18 : 1),
    };
    const initialHp = victim.state.current_hp;
    const hit = engine.resolveAttack(1, 1, owner, victim, tendril, 40, {
      setup, spendAction: false, turnKey: "1:owner",
    });
    assert.equal(hit.hit, true);
    assert.equal(victim.state.current_hp, initialHp);
    assert.ok(victim.state.active_effect_ids.includes("grappled"));
    assert.ok(victim.state.active_effect_ids.includes("restrained"));
    assert.equal(victim.position_ft, 40, "Tendril cannot silently Reel its victim.");

    // Simulate an independently reachable target, not an automatic Reel move.
    victim.position_ft = 5;
    const legalBite = formation.chooseSlotAttack(owner, setup, [bite.id]);
    assert.equal(legalBite.attack.id, bite.id);
    const bitten = engine.resolveAttack(2, 1, owner, victim, bite, 5, {
      setup, spendAction: false, turnKey: "1:owner",
    });
    assert.equal(bitten.attack_roll.mode, "advantage",
      "Restrained grants normal attack Advantage without a Roper-specific resolver.");
    assert.equal(bitten.hit, true);
    assert.ok(victim.state.current_hp < initialHp);
  } finally {
    window.IRON_PIT_DICE = savedDice;
  }
  console.log("Generic Tendril/Bite range and Restrained Advantage passed.");
} catch (error) {
  console.error("Generic Tendril/Bite range and Advantage failed.", error);
  throw error;
}
