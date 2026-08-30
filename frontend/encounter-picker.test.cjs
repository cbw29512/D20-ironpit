"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "encounter-picker.js"), "utf8"), { filename: "encounter-picker.js" });
const P = window.IRON_PIT_ENCOUNTER_PICKER;

const heroes = P.CLASS_ORDER.flatMap((classId) => [
  { id: `${classId}-1-a`, class_id: classId, class_name: classId, level: 1, build_id: "a", build_name: "A", coverage_status: "blocked", runnable_template_id: null },
  { id: `${classId}-1-b`, class_id: classId, class_name: classId, level: 1, build_id: "b", build_name: "B", coverage_status: classId === "fighter" ? "raw_ready" : "blocked", runnable_template_id: classId === "fighter" ? "fighter-runtime" : null },
]);

assert.equal(P.classOptions(heroes).length, 12);
assert.deepEqual(P.LEVELS, Array.from({ length: 20 }, (_, index) => index + 1));
assert.equal(P.heroBuilds(heroes, "fighter", 1).length, 2);
assert.equal(P.preferredHero(P.heroBuilds(heroes, "fighter", 1)).id, "fighter-1-b");
assert.equal(P.normalizedSlot(heroes, {}, { class_id: "fighter", level: 1 }).card_id, "fighter-1-b");
assert.equal(P.normalizedSlot(heroes, {}, { class_id: "wizard", level: 1 }).card_id, "wizard-1-a");

const monsters = [
  { id: "m30", name: "Tarrasque", challenge_rating: "30" },
  { id: "m2", name: "Two", challenge_rating: "2" },
  { id: "m18", name: "Eighth", challenge_rating: "1/8" },
  { id: "m1", name: "One", challenge_rating: "1" },
  { id: "m12", name: "Half", challenge_rating: "1/2" },
  { id: "m14", name: "Quarter", challenge_rating: "1/4" },
  { id: "m0", name: "Zero", challenge_rating: "0" },
];
assert.deepEqual(P.challengeRatings(monsters), ["0", "1/8", "1/4", "1/2", "1", "2", "30"]);
assert.deepEqual(P.sortedMonsters(monsters).map((monster) => monster.id), ["m0", "m18", "m14", "m12", "m1", "m2", "m30"]);
assert.deepEqual(P.sortedMonsters(monsters, "1/2").map((monster) => monster.id), ["m12"]);
assert.deepEqual(P.sortedMonsters(monsters, "30").map((monster) => monster.name), ["Tarrasque"]);

console.log("Encounter picker regressions passed through CR 30.");
