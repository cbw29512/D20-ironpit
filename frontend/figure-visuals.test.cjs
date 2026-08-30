"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "figure-visuals.js"), "utf8"), { filename: "figure-visuals.js" });
const profile = window.IRON_PIT_FIGURE_VISUALS.profile;
const p = (name, size = "medium", visual = undefined) => profile({ name, size, visual, attacks: [{ name: "Bite" }] });

assert.equal(p("Crocodile", "large").form, "reptile");
assert.equal(p("Giant Crab").form, "crab");
assert.equal(p("Constrictor Snake", "large").form, "snake");
assert.equal(p("Giant Venomous Snake").form, "snake");
assert.equal(p("Giant Wolf Spider").form, "spider");
assert.equal(p("Giant Wasp").form, "winged-insect");
assert.equal(p("Giant Centipede", "small").form, "centipede");
assert.equal(p("Wolf").form, "quadruped");
assert.equal(p("Brown Bear", "large").form, "bear");
assert.equal(p("Giant Eagle", "large").form, "bird");
assert.equal(p("Giant Bat", "large").form, "bat");
assert.equal(p("Rhinoceros", "large").detail, "horn");
assert.equal(p("Elk", "large").detail, "antlers");
assert.equal(p("Giant Goat", "large").detail, "horns");
assert.equal(p("Boar").detail, "tusks");
assert.equal(p("Ogre", "large").form, "brute");
assert.equal(p("Guard").form, "humanoid");

assert.deepEqual(
  { form: p("Owlbear", "large").form, detail: p("Owlbear", "large").detail },
  { form: "bear", detail: "owlbear" },
  "Owlbear must use the heavy hybrid silhouette, not the generic bird profile",
);
assert.deepEqual(
  { form: p("Axe Beak", "large").form, detail: p("Axe Beak", "large").detail },
  { form: "bird", detail: "beak" },
  "Axe Beak must never fall through to a humanoid silhouette",
);

const explicit = profile({
  name: "Custom Guardian", size: "medium", archetype: "Paladin",
  visual: { figure_form: "humanoid", figure_detail: "none", main_hand: "longsword", off_hand: "shield" }, attacks: [],
});
assert.equal(explicit.weapon, "longsword");
assert.equal(explicit.offHand, "shield");
assert.equal(explicit.role, "paladin");

console.log("Monster and hero stick silhouette regressions passed.");
