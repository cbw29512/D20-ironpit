"use strict";

const assert = require("node:assert/strict");

const deterministicDice = (seed = 2014) => {
  let state = seed >>> 0;
  const roll = (sides) => {
    state = (1664525 * state + 1013904223) >>> 0;
    return (state % sides) + 1;
  };
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
};

assert.equal(window.IRON_PIT_2014_MVP_READY, true, "2014 browser test roster must be loaded");
assert.equal(Object.keys(window.IRON_PIT_BROWSER_MONSTERS_2014).length, 116);
const heroes2014 = Object.values(window.IRON_PIT_BROWSER_HEROES).filter((hero) => hero.ruleset === "2014");
const fighters2014 = heroes2014.filter((hero) => hero.class_id === "fighter");
const barbarians2014 = heroes2014.filter((hero) => hero.class_id === "barbarian");
const rogues2014 = heroes2014.filter((hero) => hero.class_id === "rogue");
const monks2014 = heroes2014.filter((hero) => hero.class_id === "monk");
const paladins2014 = heroes2014.filter((hero) => hero.class_id === "paladin");
assert.equal(heroes2014.length, 60, "2014 browser hero roster must contain Fighter 1-20 plus Barbarian, Rogue, Monk, and Paladin 1-10");
assert.equal(fighters2014.length, 20);
assert.equal(barbarians2014.length, 10);
assert.equal(rogues2014.length, 10);
assert.equal(monks2014.length, 10);
assert.equal(paladins2014.length, 10);
assert.ok(fighters2014.every((hero) => hero.name === "Karnok Stoneward"));
assert.ok(barbarians2014.every((hero) => hero.name === "Rokhan Stonefury"));
assert.ok(rogues2014.every((hero) => hero.name === "Mara Quickstep"));
assert.ok(monks2014.every((hero) => hero.name === "Kael Stillwater"));
assert.ok(paladins2014.every((hero) => hero.name === "Aurelia Brightshield"));
for (const hero of heroes2014) assert.deepEqual(hero.weapon_masteries, [], `${hero.id} must not expose 2024 Weapon Mastery`);
for (const id of [
  "2014-giant-centipede", "2014-giant-poisonous-snake", "2014-giant-scorpion", "2014-giant-wasp",
  "2014-poisonous-snake", "2014-scorpion", "2014-wyvern", "2014-elk", "2014-giant-elk",
  "2014-giant-sea-horse", "2014-minotaur-skeleton", "2014-rhinoceros", "2014-allosaurus", "2014-elephant",
  "2014-mammoth", "2014-panther", "2014-saber-toothed-tiger", "2014-tiger", "2014-triceratops",
  "2014-warhorse", "2014-goat", "2014-giant-goat", "2014-mule", "2014-swarm-of-insects",
  "2014-swarm-of-poisonous-snakes", "2014-swarm-of-rats", "2014-swarm-of-ravens", "2014-noble",
  "2014-black-dragon-wyrmling", "2014-blue-dragon-wyrmling", "2014-green-dragon-wyrmling", "2014-red-dragon-wyrmling", "2014-white-dragon-wyrmling", "2014-hell-hound", "2014-chimera", "2014-young-black-dragon", "2014-young-blue-dragon", "2014-young-green-dragon", "2014-young-red-dragon",
  "2014-giant-shark", "2014-hunter-shark", "2014-quipper", "2014-swarm-of-quippers",
]) assert.ok(window.IRON_PIT_BROWSER_MONSTERS_2014[id], `${id} must be in the certified 2014 browser lane`);

for (const id of ["2014-swarm-of-insects", "2014-swarm-of-poisonous-snakes", "2014-swarm-of-rats", "2014-swarm-of-ravens"]) {
  const swarm = window.IRON_PIT_BROWSER_MONSTERS_2014[id];
  assert.equal(swarm.traits.includes("swarm"), true, `${id} must carry the shared Swarm trait`);
  assert.equal(swarm.attacks[0].conditionalDamage.trigger, "attacker_bloodied");
  assert.equal(swarm.attacks[0].conditionalDamage.mode, "replace_weapon");
}

function runCertifiedFight(heroId, expectedLevel) {
  window.IRON_PIT_DICE = deterministicDice(expectedLevel * 2014);
  const battle = window.IRON_PIT_BROWSER_ENGINE.runEncounter({
    ruleset: "2014", hero_ids: [heroId], monster_ids: ["2014-wolf", "2014-goblin"],
  });
  assert.equal(battle.ruleset, "2014");
  assert.equal(battle.setup.heroes[0].state.template.kind, "character");
  assert.equal(battle.setup.heroes[0].state.template.level, expectedLevel);
  assert.notEqual(battle.outcome, "active");
  assert.ok(battle.events.some((event) => event.event_type === "attack"));
  for (const member of [...battle.setup.heroes, ...battle.setup.monsters]) {
    assert.equal(member.state.template.ruleset, "2014", `${member.combatant_id} crossed ruleset boundary`);
  }
}

runCertifiedFight("karnok-stoneward-2014-l5", 5);
runCertifiedFight("rokhan-stonefury-2014-l5", 5);
runCertifiedFight("mara-quickstep-2014-l7", 7);
runCertifiedFight("aurelia-brightshield-2014-l6", 6);
assert.throws(
  () => window.IRON_PIT_BROWSER_ENGINE.runEncounter({
    ruleset: "2014", hero_ids: ["mara-quickstep-2014-l7"], monster_ids: ["srd-wolf"],
  }),
  /Unknown certified monster for 2014/,
);

console.log("Certified 2014 Fighter, Berserker, Thief, Open Hand Monk, and Devotion Paladin roster checks passed.");