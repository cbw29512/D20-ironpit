"use strict";
// Standard arena rows are engagement state; x/y and feet are display-only.
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

try {
  const State = window.IRON_PIT_BROWSER_STATE;
  const Formation = window.IRON_PIT_BROWSER_FORMATION;
  const Engagement = window.IRON_PIT_BROWSER_FORMATION_ENGAGEMENT;
  const Attack = window.IRON_PIT_BROWSER_ATTACK;
  const Grapple = window.IRON_PIT_BROWSER_GRAPPLE;

  const original = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-giant-crab"];
  assert.ok(original);
  const template = structuredClone(original);
  const tendril = structuredClone(template.attacks.find(a => a.controlEffect?.grappleEscapeDc));
  assert.ok(tendril);
  tendril.id = "generic-control";
  tendril.name = "Generic Control";
  tendril.kind = "melee";
  tendril.reach = 50;
  tendril.fixedDamage = 0;
  tendril.diceCount = 0;
  tendril.damageBonus = 0;
  tendril.controlEffect.grappleEscapeDc = 15;
  tendril.controlEffect.restrainsWhileGrappled = true;
  const bite = {...structuredClone(tendril), id: "generic-bite", name: "Generic Bite",
    reach: 5, fixedDamage: 4, controlEffect: null,
    forbidSelfGrappledTarget: false, grappleTargetPolicy: "normal"};
  const bow = {...structuredClone(bite), id: "generic-bow", name: "Generic Bow",
    kind: "ranged", normal: 80, long: 320};
  template.attacks = [tendril, bite, bow];
  const make = (id, side, row, position_ft) => {
    const state = State.buildState(structuredClone(template));
    state.formation_row = row;
    return {combatant_id: id, side, position_ft, state};
  };
  const source = make("source", "monsters", "front", 0);
  const victim = make("victim", "heroes", "front", 40);
  const setup = {heroes: [victim], monsters: [source], arena_mode: "formation"};
  const teammate = make("teammate", "monsters", "front", 50);
  setup.monsters.push(teammate);
  source.state.template.traits = [...(source.state.template.traits || []), "pack-tactics"];
  assert.equal(State.hasAdjacentActiveAlly(source, victim, setup), true);
  assert.equal(State.packTactics(source, victim, setup), true);

  assert.equal(Engagement.effectiveRow(victim, setup), "front");
  assert.equal(Formation.chooseSlotAttack(source, setup, [bite.id]).attack.id, bite.id);
  assert.equal(Formation.chooseSlotAttack(source, setup, [tendril.id]).distance, 5);

  const dice = window.IRON_PIT_DICE;
  try {
    window.IRON_PIT_DICE = {
      roll: sides => sides === 20 ? 18 : 1,
      rollMany: (count, sides) => Array.from({length: count}, () => sides === 20 ? 18 : 1),
    };
    const hp = victim.state.current_hp;
    const first = Attack.resolveAttack(1, 1, source, victim, tendril, 40, {
      setup, spendAction: false, turnKey: "1:source",
    });
    assert.equal(first.hit, true);
    assert.equal(victim.state.current_hp, hp);
    assert.ok(victim.state.active_effect_ids.includes("grappled"));
    assert.ok(victim.state.active_effect_ids.includes("restrained"));
    Grapple.cleanup(setup);
    assert.ok(victim.state.active_effect_ids.includes("grappled"));
    assert.equal(victim.position_ft, 40);
    const followup = Attack.resolveAttack(2, 1, source, victim, bite, 40, {
      setup, spendAction: false, turnKey: "1:source",
    });
    assert.equal(followup.attack_roll.mode, "advantage");
    assert.equal(followup.hit, true);
    assert.ok(victim.state.current_hp < hp);
  } finally {
    window.IRON_PIT_DICE = dice;
  }

  const allyFront = make("ally-front", "monsters", "front", 5);
  const back = make("back", "monsters", "back", 25);
  const enemy = make("enemy", "heroes", "front", 40);
  const second = {heroes: [enemy], monsters: [allyFront, back], arena_mode: "formation"};
  assert.equal(Engagement.effectiveRow(back, second), "back");
  assert.equal(Formation.chooseSlotAttack(back, second, [bite.id]), null);
  assert.ok(Formation.chooseSlotAttack(back, second, [bow.id]));
  allyFront.state.current_hp = 0;
  allyFront.state.is_dead = true;
  allyFront.state.is_alive = false;
  assert.equal(Engagement.effectiveRow(back, second), "front");
  assert.equal(Formation.chooseSlotAttack(back, second, [bite.id]).attack.id, bite.id);
  assert.equal(back.state.formation_row, "back",
    "Immediate eligibility does not require moving a displayed card.");
  assert.equal(template.attacks.length, 3);
  console.log("Universal formation-only weapon engagement and promotion passed.");
} catch (error) {
  console.error("Universal formation weapon engagement regression failed.", error);
  throw error;
}
