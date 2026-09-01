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

console.log("Generated browser monsters expose source-backed creature types for deterministic targeting.");
