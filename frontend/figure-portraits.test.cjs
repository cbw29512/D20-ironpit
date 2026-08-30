"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of ["figure-profiles.js", "figure-visuals.js", "figure-portraits.js"]) load(file);

const P = window.IRON_PIT_FIGURE_PORTRAITS;
const monster = (name, size = "medium") => ({ name, kind: "monster", size, attacks: [{ name: "Bite" }] });

const owlbear = P.markup(monster("Owlbear", "large"));
const owl = P.markup(monster("Giant Owl", "large"));
const snake = P.markup(monster("Giant Constrictor Snake", "huge"));

assert.match(owlbear, /<svg class="portrait-svg"/);
assert.match(owlbear, /<ellipse|<circle|<path/);
assert.doesNotMatch(owlbear, /class="head"|class="body"|class="arms"|class="legs"/);
assert.notEqual(owlbear, owl, "Owlbear and Giant Owl must not share the same portrait silhouette.");
assert.match(snake, /stroke-linecap="round"/, "Snake portrait should use a coiled silhouette.");

const hero = P.markup({
  name: "Audited Paladin", kind: "character", size: "medium", archetype: "Paladin",
  visual: { figure_form: "humanoid", figure_detail: "paladin", main_hand: "longsword", off_hand: "shield" }, attacks: [],
});
assert.match(hero, /Audited Paladin/);
assert.match(hero, /portrait-ink/);

console.log("Fantasy portrait renderer regressions passed.");
