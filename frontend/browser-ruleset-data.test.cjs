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

load("browser-heroes.js");
load("browser-monsters-generated.js");
assertRuleset(Object.values(window.IRON_PIT_BROWSER_HEROES), "2024", "canonical browser heroes");
assertRuleset(Object.values(window.IRON_PIT_BROWSER_MONSTERS), "2024", "canonical browser monsters");
for (const fixture of [
  "browser-monsters.js", "browser-monsters-fixed.js", "browser-monsters-beast2.js",
  "browser-monsters-batch3.js", "browser-monsters-control.js", "browser-monsters-expansion.js",
  "browser-monsters-venom.js", "browser-monsters-mixed.js", "browser-monsters-poison.js",
]) load(fixture);
assertRuleset(Object.values(window.IRON_PIT_BROWSER_MONSTERS), "2024", "legacy browser monster fixtures");

load("browser-heroes-2014.js");
const heroes2014 = Object.values(window.IRON_PIT_BROWSER_HEROES_2014);
assert.equal(heroes2014.length, 10, "2014 browser hero roster must contain Karnok levels 1 through 10");
assertRuleset(heroes2014, "2014", "2014 browser heroes");
assert.equal(window.IRON_PIT_2014_HEROES_READY, true);
assert.deepEqual(heroes2014.map((hero) => hero.level).sort((a, b) => a - b), [1,2,3,4,5,6,7,8,9,10]);
for (const hero of heroes2014) {
  assert.equal(hero.kind, "character", `${hero.id} must remain a character`);
  assert.deepEqual(hero.weapon_masteries, [], `${hero.id} must not leak 2024 Weapon Mastery`);
  for (const attack of hero.attacks) {
    assert.equal(Object.hasOwn(attack, "masteryProperty"), false, `${hero.id}:${attack.id} must not contain mastery metadata`);
  }
}
const karnok3 = window.IRON_PIT_BROWSER_HEROES_2014["karnok-stoneward-2014-l3"];
const karnok5 = window.IRON_PIT_BROWSER_HEROES_2014["karnok-stoneward-2014-l5"];
const karnok7 = window.IRON_PIT_BROWSER_HEROES_2014["karnok-stoneward-2014-l7"];
const karnok10 = window.IRON_PIT_BROWSER_HEROES_2014["karnok-stoneward-2014-l10"];
assert.equal(karnok3.critical_hit_minimum, 19, "2014 Champion Improved Critical begins at level 3");
assert.equal(karnok5.attack_action.slots.length, 2, "2014 Fighter Extra Attack begins at level 5");
assert.equal(karnok7.initiative_bonus, 4, "2014 Remarkable Athlete must affect initiative");
assert.deepEqual(karnok10.fighting_styles, ["Defense", "Archery"]);
const longbow10 = karnok10.attacks.find((attack) => attack.weaponId === "longbow");
assert.ok(longbow10, "2014 level 10 Fighter must expose the certified longbow");
assert.equal(longbow10.bonus, 8, "Archery Fighting Style must add +2 to the level 10 longbow attack");

load("browser-monsters-2014.js");
const monsters2014 = Object.values(window.IRON_PIT_BROWSER_MONSTERS_2014);
assert.equal(monsters2014.length, 100, "2014 browser roster must contain exactly 100 certified monsters");
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
  "2014-poisonous-snake", "2014-scorpion", "2014-wyvern",
  "2014-elk", "2014-giant-elk", "2014-giant-sea-horse", "2014-minotaur-skeleton", "2014-rhinoceros",
  "2014-allosaurus", "2014-elephant", "2014-mammoth", "2014-panther", "2014-saber-toothed-tiger",
  "2014-tiger", "2014-triceratops", "2014-warhorse",
  "2014-goat", "2014-giant-goat",
  "2014-swarm-of-insects", "2014-swarm-of-poisonous-snakes", "2014-swarm-of-rats", "2014-swarm-of-ravens",
]) {
  assert.ok(monsters2014.some((monster) => monster.id === id), `${id} must exist in the 2014 browser roster`);
}
for (const id of [
  "2014-swarm-of-insects", "2014-swarm-of-poisonous-snakes", "2014-swarm-of-rats", "2014-swarm-of-ravens",
]) {
  const swarm = monsters2014.find((monster) => monster.id === id);
  assert.ok(swarm, `${id} must exist before source-shape assertions`);
  assert.equal(swarm.traits.includes("swarm"), true);
  assert.equal(swarm.attacks[0].conditionalDamage.trigger, "attacker_bloodied");
  assert.equal(swarm.attacks[0].conditionalDamage.mode, "replace_weapon");
}
const mule = monsters2014.find((monster) => monster.id === "2014-mule");
assert.ok(mule, "2014-mule must exist before trait assertions");
assert.deepEqual(mule.traits, ["sure-footed"], "Beast of Burden stays arena-neutral while Sure-Footed remains modeled");
assertRuleset(monsters2014, "2014", "2014 browser monsters");
assert.equal(window.IRON_PIT_2014_MVP_READY, true);
console.log("Browser combatants carry explicit isolated ruleset identity for 2014 and 2024.");
