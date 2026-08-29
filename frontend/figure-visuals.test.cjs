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
assert.equal(profile({ name: "Karnok", size: "medium", visual: { main_hand: "greatsword" }, attacks: [] }).weapon, "greatsword");

console.log("Monster stick silhouette regressions passed.");
