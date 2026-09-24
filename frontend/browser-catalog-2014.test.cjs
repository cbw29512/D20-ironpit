"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

load("browser-heroes.js");
load("browser-monsters-2014.js");
load("browser-catalog.js");

(async () => {
  const catalog = await window.IRON_PIT_BROWSER_CATALOG.buildCatalog("2014");
  assert.equal(catalog.ruleset, "2014");
  assert.equal(catalog.test_lane, true);
  assert.equal(catalog.hero_count, 240);
  assert.equal(catalog.hero_ready_count, catalog.heroes.length);
  assert.equal(catalog.monster_count, 327);
  assert.equal(catalog.monster_ready_count, catalog.monsters.length);
  assert.equal(catalog.heroes.length, catalog.hero_ready_count);
  assert.equal(catalog.monsters.length, catalog.monster_ready_count);
  assert.ok(catalog.heroes.every((card) => card.ruleset === "2014" && card.kind === "character"));
  assert.ok(catalog.monsters.every((card) => card.ruleset === "2014" && card.kind === "monster"));
  const fighters = catalog.heroes.filter((card) => card.class_id === "fighter");
  const barbarians = catalog.heroes.filter((card) => card.class_id === "barbarian");
  const rogues = catalog.heroes.filter((card) => card.class_id === "rogue");
  const monks = catalog.heroes.filter((card) => card.class_id === "monk");
  const paladins = catalog.heroes.filter((card) => card.class_id === "paladin");
  const clerics = catalog.heroes.filter((card) => card.class_id === "cleric");
  assert.deepEqual(fighters.map((card) => card.level), Array.from({ length: 20 }, (_, i) => i + 1));
  assert.deepEqual(barbarians.map((card) => card.level), Array.from({ length: 20 }, (_, i) => i + 1));
  assert.deepEqual(rogues.map((card) => card.level), Array.from({ length: 20 }, (_, i) => i + 1));
  assert.deepEqual(monks.map((card) => card.level), Array.from({ length: 20 }, (_, i) => i + 1));
  assert.deepEqual(paladins.map((card) => card.level), Array.from({ length: 12 }, (_, i) => i + 1));
  assert.deepEqual(
    clerics.map((card) => card.level),
    Array.from({ length: clerics.length }, (_, i) => i + 1),
    "2014 Life Cleric catalog must remain one continuous persistent progression",
  );
  assert.ok(fighters.every((card) => card.name === "Karnok Stoneward"));
  assert.ok(barbarians.every((card) => card.name === "Rokhan Stonefury"));
  assert.ok(rogues.every((card) => card.name === "Mara Quickstep"));
  assert.ok(monks.every((card) => card.name === "Kael Stillwater"));
  assert.ok(paladins.every((card) => card.name === "Aurelia Brightshield"));
  assert.ok(clerics.every((card) => card.name === "Seraphine Dawnshield"));
  assert.equal(fighters.find((card) => card.level === 3).subclass_id, "champion");
  assert.equal(barbarians.find((card) => card.level === 3).subclass_id, "path-berserker");
  assert.equal(rogues.find((card) => card.level === 3).subclass_id, "thief");
  assert.equal(monks.find((card) => card.level === 3).subclass_id, "way-open-hand");
  assert.equal(paladins.find((card) => card.level === 3).subclass_id, "oath-devotion");
  assert.equal(clerics.find((card) => card.level === 3).subclass_id, "life-domain");
  assert.ok(catalog.heroes.every((card) => card.build_id === "canonical-2014"));
  console.log("2014 catalog exposes the certified persistent progressions, including the current Life Cleric progression.");
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});