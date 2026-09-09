"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const source = fs.readFileSync(path.join(__dirname, "browser-monsters-generated.js"), "utf8");
vm.runInThisContext(source, { filename: "browser-monsters-generated.js" });

const monsters = window.IRON_PIT_BROWSER_MONSTERS;
assert.equal(window.IRON_PIT_CANONICAL_MONSTERS_READY, true);
assert.ok(monsters && Object.keys(monsters).length > 0);
for (const monster of Object.values(monsters)) {
  assert.equal(typeof monster.creature_type, "string", `${monster.id} must export creature_type`);
  assert.ok(monster.creature_type.trim().length > 0, `${monster.id} creature_type must not be blank`);
}
assert.equal(monsters["srd-skeleton"].creature_type, "Undead");
assert.equal(monsters["srd-ogre-zombie"].creature_type, "Undead");
assert.equal(monsters["srd-goblin-warrior"].creature_type, "Fey (Goblinoid)");
assert.notEqual(monsters["srd-goblin-warrior"].creature_type, "Undead");

const reef = monsters["srd-reef-shark"];
assert.ok(reef, "srd-reef-shark must be certified under the hospitable-arena policy");
assert.deepEqual(reef.source_trait_names, ["Pack Tactics", "Water Breathing"]);
assert.ok(reef.traits.includes("pack-tactics"), "srd-reef-shark must export Pack Tactics into runtime combat data");
assert.ok(reef.movement_modes.swim_ft > 0, "srd-reef-shark must preserve its source swim movement");

for (const id of [
  "srd-giant-shark", "srd-hunter-shark", "srd-piranha", "srd-swarm-of-piranhas",
]) {
  const monster = monsters[id];
  assert.ok(monster, `${id} must be certified once target-missing-hp Advantage is modeled`);
  assert.deepEqual(monster.attacks[0].conditionalAttackModifiers, [
    { trigger: "target_missing_hp", mode: "advantage" },
  ]);
}

const specter = monsters["srd-specter"];
assert.ok(specter, "srd-specter must preserve its full source trait fingerprint while Incorporeal Movement is arena-irrelevant");
assert.deepEqual(specter.source_trait_names, ["Incorporeal Movement", "Sunlight Sensitivity"]);
assert.equal(specter.movement_modes.fly_ft > 0, true, "srd-specter must preserve its printed flight movement");

const wraith = monsters["srd-wraith"];
assert.ok(wraith, "srd-wraith must preserve its full source trait fingerprint while Incorporeal Movement is arena-irrelevant");
assert.deepEqual(wraith.source_trait_names, ["Incorporeal Movement", "Sunlight Sensitivity"]);
assert.equal(wraith.movement_modes.fly_ft > 0, true, "srd-wraith must preserve its printed flight movement");

console.log("Generated browser monsters preserve creature type, movement, combat traits, and complete source trait fingerprints.");