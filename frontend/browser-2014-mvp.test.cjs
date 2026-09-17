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
assert.equal(Object.keys(window.IRON_PIT_BROWSER_MONSTERS_2014).length, 100);
const heroes2014 = Object.values(window.IRON_PIT_BROWSER_HEROES).filter((hero) => hero.ruleset === "2014");
assert.equal(heroes2014.length, 10, "2014 browser hero roster must contain Karnok levels 1-10");
for (const hero of heroes2014) {
  assert.equal(hero.name, "Karnok Stoneward");
  assert.deepEqual(hero.weapon_masteries, [], `${hero.id} must not expose 2024 Weapon Mastery`);
}
for (const id of [
  "2014-giant-centipede", "2014-giant-poisonous-snake", "2014-giant-scorpion", "2014-giant-wasp",
  "2014-poisonous-snake", "2014-scorpion", "2014-wyvern",
  "2014-elk", "2014-giant-elk", "2014-giant-sea-horse", "2014-minotaur-skeleton", "2014-rhinoceros",
  "2014-allosaurus", "2014-elephant", "2014-mammoth", "2014-panther", "2014-saber-toothed-tiger",
  "2014-tiger", "2014-triceratops", "2014-warhorse",
  "2014-goat", "2014-giant-goat", "2014-mule",
  "2014-swarm-of-insects", "2014-swarm-of-poisonous-snakes", "2014-swarm-of-rats", "2014-swarm-of-ravens",
]) assert.ok(window.IRON_PIT_BROWSER_MONSTERS_2014[id], `${id} must be in the certified 2014 browser lane`);

for (const id of [
  "2014-swarm-of-insects", "2014-swarm-of-poisonous-snakes", "2014-swarm-of-rats", "2014-swarm-of-ravens",
]) {
  const swarm = window.IRON_PIT_BROWSER_MONSTERS_2014[id];
  assert.equal(swarm.traits.includes("swarm"), true, `${id} must carry the shared Swarm trait`);
  assert.equal(swarm.attacks[0].conditionalDamage.trigger, "attacker_bloodied");
  assert.equal(swarm.attacks[0].conditionalDamage.mode, "replace_weapon");
}

window.IRON_PIT_DICE = deterministicDice();
const battle = window.IRON_PIT_BROWSER_ENGINE.runEncounter({
  ruleset: "2014",
  hero_ids: ["karnok-stoneward-2014-l5"],
  monster_ids: ["2014-wolf", "2014-goblin"],
});

assert.equal(battle.ruleset, "2014");
assert.equal(battle.setup.heroes[0].state.template.kind, "character");
assert.equal(battle.setup.heroes[0].state.template.level, 5);
assert.notEqual(battle.outcome, "active");
assert.ok(battle.events.some((event) => event.event_type === "attack"));
for (const member of [...battle.setup.heroes, ...battle.setup.monsters]) {
  assert.equal(member.state.template.ruleset, "2014", `${member.combatant_id} crossed ruleset boundary`);
}
assert.throws(
  () => window.IRON_PIT_BROWSER_ENGINE.runEncounter({
    ruleset: "2014",
    hero_ids: ["karnok-stoneward-2014-l5"],
    monster_ids: ["srd-wolf"],
  }),
  /Unknown certified monster for 2014/,
);

console.log("Certified 2014 Fighter-vs-monster browser fight passed.");
