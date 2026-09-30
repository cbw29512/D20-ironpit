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

const hero = window.IRON_PIT_BROWSER_HEROES["thalen-greenbough-l11"];
assert.ok(hero, "2024 Druid 11 must exist in generated browser heroes.");
assert.equal(hero.level, 11);
assert.equal(hero.max_hp, 58);
assert.deepEqual(hero.damage_resistances, ["fire"]);
assert.deepEqual(hero.condition_immunities, ["poisoned"]);
assert.deepEqual(hero.resources, {
  "spell-slot-1": 4,
  "spell-slot-2": 3,
  "spell-slot-3": 3,
  "spell-slot-4": 3,
  "spell-slot-5": 2,
  "spell-slot-6": 1,
  "wild-shape": 3,
  "wild-resurgence-slot-restore": 1,
  "natural-recovery-free-cast": 1,
});

assert.equal(hero.canonical_prepared_spells.length, 16);
assert.equal(hero.canonical_prepared_spells.at(-1).id, "heal");

const heal = hero.healingActions.find((item) => item.id === "heal");
assert.ok(heal, "Druid 11 must expose 2024 Heal.");
assert.equal(heal.actionCost, "action");
assert.equal(heal.range, 60);
assert.equal(heal.targetMode, "self_or_ally");
assert.equal(heal.diceCount, 0);
assert.equal(heal.healingBonus, 70);
assert.equal(heal.resourceId, "spell-slot-6");
assert.equal(heal.resourceCost, 1);
assert.deepEqual(heal.removableConditions, ["blinded", "deafened", "poisoned"]);

console.log("Generated browser 2024 Druid 11 progression regressions passed.");
