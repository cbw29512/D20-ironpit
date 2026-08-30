"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
for (const file of [
  "browser-pregen-data.js", "browser-pregen-math.js", "browser-pregen-attacks.js",
  "browser-pregen-spells.js", "browser-pregen-factory.js", "browser-heroes.js",
]) vm.runInThisContext(fs.readFileSync(path.join(__dirname, file), "utf8"), { filename: file });

const heroes = Object.values(window.IRON_PIT_BROWSER_HEROES);
const key = (hero) => `${hero.class_id}:${hero.level}:${hero.build_id}`;
const byKey = new Map(heroes.map((hero) => [key(hero), hero]));
const D = window.IRON_PIT_PREGEN_DATA;

assert.equal(heroes.length, 720, "12 classes × 20 levels × 3 builds must all have runtime templates");
assert.equal(byKey.size, 720, "every class/level/build must be unique");
for (const [classId] of D.CLASS_ROWS) for (let level = 1; level <= 20; level += 1) {
  for (const [buildId] of D.BUILD_ROWS[classId]) {
    const hero = byKey.get(`${classId}:${level}:${buildId}`);
    assert.ok(hero, `missing ${classId} ${level} ${buildId}`);
    assert.ok(hero.max_hp > 0 && hero.armor_class > 0 && hero.speed_ft > 0);
    assert.equal(Object.keys(hero.saving_throw_bonuses).length, 6);
    assert.ok(hero.attacks.length || hero.saving_throw_actions.length, `${hero.name} needs a legal offensive action`);
  }
}

const wizard1 = byKey.get("wizard:1:evoker"), wizard17 = byKey.get("wizard:17:evoker");
assert.equal(wizard1.attacks[0].name, "Fire Bolt");
assert.equal(wizard1.attacks[0].diceCount, 1);
assert.equal(wizard17.attacks[0].diceCount, 4);
assert.ok(wizard17.attacks[0].bonus > wizard1.attacks[0].bonus);

const fighter5 = byKey.get("fighter:5:guardian"), fighter11 = byKey.get("fighter:11:guardian"), fighter20 = byKey.get("fighter:20:guardian");
assert.equal(fighter5.attack_action.slots.length, 2);
assert.equal(fighter11.attack_action.slots.length, 3);
assert.equal(fighter20.attack_action.slots.length, 4);
assert.match(fighter5.attacks[0].name, /^\+1 /);
assert.match(fighter11.attacks[0].name, /^\+2 /);
assert.match(fighter20.attacks[0].name, /^\+3 /);

const cleric5 = byKey.get("cleric:5:healer");
assert.equal(cleric5.saving_throw_actions[0].name, "Sacred Flame");
assert.equal(cleric5.healingActions[0].name, "Healing Word");
assert.equal(cleric5.resources["healing-word-slot"], 4);

const paladin7 = byKey.get("paladin:7:guardian");
assert.equal(paladin7.healingActions[0].name, "Lay on Hands");
assert.equal(paladin7.resources["lay-on-hands-points"], 35);

const sorcerer6 = byKey.get("sorcerer:6:blaster");
assert.ok(sorcerer6.damage_resistances.includes("fire"));
assert.equal(sorcerer6.armor_class, 10 + Math.floor((sorcerer6.ability_scores.dexterity - 10) / 2) + Math.floor((sorcerer6.ability_scores.charisma - 10) / 2));

assert.ok(byKey.get("fighter:1:great-weapon").full_feature_coverage);
assert.ok(byKey.get("barbarian:1:great-weapon").full_feature_coverage);
assert.equal(byKey.get("wizard:1:evoker").automation_coverage, "core-raw");

console.log("Complete pregen runtime roster regressions passed.");
