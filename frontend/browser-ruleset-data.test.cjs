"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
const assertRuleset = (items, expected, label) => {
  assert.ok(items.length > 0, `${label} must not be empty`);
  for (const item of items) assert.equal(item.ruleset, expected, `${item.id} must carry explicit ${expected} ruleset identity`);
};
const levels = (items, count) => assert.deepEqual(items.map((item) => item.level).sort((a, b) => a - b), Array.from({ length: count }, (_, i) => i + 1));

load("browser-heroes.js");
load("browser-monsters-generated.js");
const browserHeroes = Object.values(window.IRON_PIT_BROWSER_HEROES);
const heroes2024 = browserHeroes.filter((hero) => hero.ruleset === "2024");
const heroes2014 = browserHeroes.filter((hero) => hero.ruleset === "2014");
const fighters2014 = heroes2014.filter((hero) => hero.class_id === "fighter");
const barbarians2014 = heroes2014.filter((hero) => hero.class_id === "barbarian");
const rogues2014 = heroes2014.filter((hero) => hero.class_id === "rogue");
const monks2014 = heroes2014.filter((hero) => hero.class_id === "monk");
const paladins2014 = heroes2014.filter((hero) => hero.class_id === "paladin");
assertRuleset(heroes2024, "2024", "2024 browser heroes");
assertRuleset(heroes2014, "2014", "2014 browser heroes");
assert.equal(heroes2014.length, 60, "2014 browser heroes must contain Fighter 1-20 plus Barbarian, Rogue, Monk, and Paladin 1-10");
levels(fighters2014, 20); levels(barbarians2014, 10); levels(rogues2014, 10); levels(monks2014, 10); levels(paladins2014, 10);
for (const hero of heroes2014) {
  assert.deepEqual(hero.weapon_masteries, [], `${hero.id} must not expose 2024 Weapon Mastery`);
  assert.ok(hero.attacks.every((attack) => attack.masteryProperty == null), `${hero.id} attacks must not carry mastery properties`);
}
const fighter15 = fighters2014.find((hero) => hero.level === 15);
const fighter18 = fighters2014.find((hero) => hero.level === 18);
const fighter20 = fighters2014.find((hero) => hero.level === 20);
assert.equal(fighter15.critical_hit_minimum, 18);
assert.equal(fighter18.survivor_heal_amount, 9);
assert.equal(fighter20.survivor_heal_amount, 10);
assert.equal(fighter20.attack_action.slots.length, 4);
const barbarian3 = barbarians2014.find((hero) => hero.level === 3);
const barbarian9 = barbarians2014.find((hero) => hero.level === 9);
const barbarian10 = barbarians2014.find((hero) => hero.level === 10);
assert.equal(barbarian3.frenzy_bonus_attack_2014, true);
assert.equal(barbarian9.brutal_critical_dice, 1);
assert.ok(barbarian10.intimidating_presence_2014_dc > 0);
const rogue2 = rogues2014.find((hero) => hero.level === 2);
const rogue5 = rogues2014.find((hero) => hero.level === 5);
const rogue7 = rogues2014.find((hero) => hero.level === 7);
const rogue10 = rogues2014.find((hero) => hero.level === 10);
assert.equal(rogue2.cunning_action, true);
assert.equal(rogue5.uncanny_dodge, true);
assert.equal(rogue7.evasion, true);
assert.equal(rogue10.sneak_attack_d6, 5);
const monk2 = monks2014.find((hero) => hero.level === 2);
const monk5 = monks2014.find((hero) => hero.level === 5);
const monk7 = monks2014.find((hero) => hero.level === 7);
const monk10 = monks2014.find((hero) => hero.level === 10);
assert.equal(monk2.flurry_of_blows, true);
assert.equal(monk5.stunning_strike, true);
assert.equal(monk7.evasion, true);
assert.deepEqual(monk10.condition_immunities, ["poisoned"]);
const paladin3 = paladins2014.find((hero) => hero.level === 3);
const paladin6 = paladins2014.find((hero) => hero.level === 6);
const paladin10 = paladins2014.find((hero) => hero.level === 10);
assert.equal(paladin3.divine_smite_2014, true);
assert.equal(paladin3.turn_unholy_2014, true);
assert.ok(paladin6.aura_of_protection_2014_bonus > 0);
assert.equal(paladin10.aura_of_courage_2014, true);
assertRuleset(Object.values(window.IRON_PIT_BROWSER_MONSTERS), "2024", "canonical browser monsters");
for (const fixture of [
  "browser-monsters.js", "browser-monsters-fixed.js", "browser-monsters-beast2.js",
  "browser-monsters-batch3.js", "browser-monsters-control.js", "browser-monsters-expansion.js",
  "browser-monsters-venom.js", "browser-monsters-mixed.js", "browser-monsters-poison.js",
]) load(fixture);
assertRuleset(Object.values(window.IRON_PIT_BROWSER_MONSTERS), "2024", "legacy browser monster fixtures");

load("browser-monsters-2014.js");
const monsters2014 = Object.values(window.IRON_PIT_BROWSER_MONSTERS_2014);
assert.equal(monsters2014.length, 127, "2014 browser roster must contain exactly 127 certified monsters");
for (const id of [
  "2014-bandit", "2014-brown-bear", "2014-goblin", "2014-skeleton", "2014-fire-giant", "2014-owlbear",
  "2014-badger", "2014-cat", "2014-crab", "2014-hawk", "2014-lizard", "2014-rat", "2014-weasel",
  "2014-baboon", "2014-blood-hawk", "2014-giant-rat", "2014-ogre-zombie", "2014-raven", "2014-zombie",
  "2014-awakened-shrub", "2014-awakened-tree", "2014-giant-fire-beetle", "2014-giant-owl",
  "2014-kobold", "2014-mule", "2014-owl", "2014-pteranodon", "2014-twig-blight",
  "2014-constrictor-snake", "2014-crocodile", "2014-flying-snake", "2014-giant-constrictor-snake",
  "2014-giant-crab", "2014-roc", "2014-tyrannosaurus-rex",
  "2014-ankylosaurus", "2014-dire-wolf", "2014-giant-crocodile", "2014-mastiff", "2014-wolf", "2014-worg",
  "2014-giant-centipede", "2014-giant-poisonous-snake", "2014-giant-scorpion", "2014-giant-wasp",
  "2014-poisonous-snake", "2014-scorpion", "2014-wyvern", "2014-elk", "2014-giant-elk",
  "2014-giant-sea-horse", "2014-minotaur-skeleton", "2014-rhinoceros", "2014-allosaurus", "2014-elephant",
  "2014-mammoth", "2014-panther", "2014-saber-toothed-tiger", "2014-tiger", "2014-triceratops",
  "2014-warhorse", "2014-goat", "2014-giant-goat", "2014-swarm-of-insects", "2014-swarm-of-poisonous-snakes",
  "2014-swarm-of-rats", "2014-swarm-of-ravens", "2014-noble",
  "2014-black-dragon-wyrmling", "2014-blue-dragon-wyrmling", "2014-green-dragon-wyrmling",
  "2014-red-dragon-wyrmling", "2014-white-dragon-wyrmling", "2014-hell-hound", "2014-chimera",
  "2014-young-black-dragon", "2014-young-blue-dragon", "2014-young-green-dragon", "2014-young-red-dragon",
  "2014-giant-shark", "2014-hunter-shark", "2014-quipper", "2014-swarm-of-quippers",
  "2014-giant-wolf-spider", "2014-spider", "2014-lion", "2014-young-white-dragon",
  "2014-bat", "2014-giant-bat", "2014-killer-whale", "2014-swarm-of-bats",
  "2014-berserker", "2014-minotaur", "2014-winter-wolf",
]) assert.ok(monsters2014.some((monster) => monster.id === id), `${id} must exist in the 2014 browser roster`);
for (const id of ["2014-swarm-of-insects", "2014-swarm-of-poisonous-snakes", "2014-swarm-of-rats", "2014-swarm-of-ravens"]) {
  const swarm = monsters2014.find((monster) => monster.id === id);
  assert.ok(swarm); assert.equal(swarm.traits.includes("swarm"), true);
  assert.equal(swarm.attacks[0].conditionalDamage.trigger, "attacker_bloodied");
  assert.equal(swarm.attacks[0].conditionalDamage.mode, "replace_weapon");
}
for (const id of ["2014-giant-shark", "2014-hunter-shark", "2014-quipper", "2014-swarm-of-quippers"]) {
  const monster = monsters2014.find((item) => item.id === id);
  assert.ok(monster);
  assert.deepEqual(monster.attacks[0].conditionalAttackAdvantage, [{ trigger: "target_not_full_hp" }]);
}
const mule = monsters2014.find((monster) => monster.id === "2014-mule");
assert.ok(mule); assert.deepEqual(mule.traits, ["sure-footed"]);
const noble = monsters2014.find((monster) => monster.id === "2014-noble");
assert.ok(noble); assert.deepEqual(noble.parry_reaction, { ac_bonus: 2 });
const recoveredHellHound = monsters2014.find((monster) => monster.id === "2014-hell-hound");
assert.ok(recoveredHellHound);
const recoveredBreath = recoveredHellHound.saving_throw_actions.find((action) => action.id === "fire-breath");
assert.equal(recoveredBreath.area.shape, "cone");
assert.equal(recoveredBreath.area.length_ft, 15);
assert.equal(recoveredBreath.resourceId, "fire-breath");
assert.equal(recoveredHellHound.resources["fire-breath"], 1);
assert.deepEqual(recoveredHellHound.recharge_rules, [{ resourceId: "fire-breath", minimumRoll: 5, dieSize: 6 }]);
assertRuleset(monsters2014, "2014", "2014 browser monsters");
assert.equal(window.IRON_PIT_2014_MVP_READY, true);
console.log("Browser combatants carry explicit isolated ruleset identity for 2014 and 2024.");