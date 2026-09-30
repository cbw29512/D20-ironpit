"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

load("browser-heroes.js");

const hero = window.IRON_PIT_BROWSER_HEROES["thalen-greenbough-l13"];
assert.ok(hero, "2024 Druid 13 must exist in generated browser heroes.");
assert.equal(hero.level, 13);
assert.equal(hero.max_hp, 68);
assert.equal(hero.ability_scores.wisdom, 20);
assert.equal(hero.ability_scores.charisma, 18);
assert.deepEqual(hero.damage_resistances, ["fire"]);
assert.deepEqual(hero.condition_immunities, ["poisoned"]);
assert.deepEqual(hero.resources, {
  "spell-slot-1": 4,
  "spell-slot-2": 3,
  "spell-slot-3": 3,
  "spell-slot-4": 3,
  "spell-slot-5": 2,
  "spell-slot-6": 1,
  "spell-slot-7": 1,
  "wild-shape": 3,
  "wild-resurgence-slot-restore": 1,
  "natural-recovery-free-cast": 1,
});
assert.equal(hero.canonical_prepared_spells.length, 17);
assert.equal(hero.canonical_prepared_spells.at(-1).id, "fire-storm");
assert.equal(
  hero.spell_save_actions.some((item) => item.id === "fire-storm"),
  false,
  "Fire Storm must not be approximated before multi-cube geometry exists.",
);

console.log("Generated browser 2024 Druid 13 progression regressions passed.");
