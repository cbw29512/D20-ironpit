"use strict";

require("./combatant-art.test.cjs");

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
assert.equal(P.keyFor(monster("Goblin"), { form: "unknown", detail: "none" }), "goblin");
assert.equal(P.keyFor(monster("Skeleton"), { form: "humanoid", detail: "skeleton" }), "skeleton");
assert.equal(P.keyFor(monster("Unicorn", "large"), { form: "unknown", detail: "none" }), "unicorn");
assert.equal(P.keyFor(monster("Giant Shark", "huge"), { form: "fish", detail: "shark" }), "fish");
assert.notEqual(P.markup(monster("Goblin")), P.markup(monster("Skeleton")));
assert.match(P.markup(monster("Goblin")), /M28 22 18 10/, "Goblin portrait must keep pointed ears.");
assert.match(P.markup(monster("Goblin")), /M64 50c16-12/, "Goblin portrait must include a scimitar.");
assert.notEqual(P.markup(monster("Unicorn", "large")), P.markup(monster("Riding Horse", "large")));
assert.equal(P.keyFor(monster("Troll", "large"), { form: "brute", detail: "troll" }), "troll");
assert.match(P.markup(monster("Troll", "large")), /M22 88 36 48/, "Troll portrait must reuse the existing long-limbed silhouette.");
assert.notEqual(P.markup(monster("Troll", "large")), P.markup(monster("Ogre", "large")));
assert.notEqual(P.markup(monster("Troll", "large")), P.markup(monster("Hill Giant", "huge")));
const trollCss = fs.readFileSync(path.join(__dirname, "figure-archetypes.css"), "utf8");
assert.match(trollCss, /\[data-form="brute"\]\[data-detail="troll"\]/, "Troll stick-figure must keep a hunched long-limbed identity.");

const hero = P.markup({
  name: "Audited Paladin", kind: "character", size: "medium", archetype: "Paladin",
  visual: { figure_form: "humanoid", figure_detail: "paladin", main_hand: "longsword", off_hand: "shield" }, attacks: [],
});
assert.match(hero, /Audited Paladin/);
assert.match(hero, /portrait-ink/);

console.log("Fantasy portrait renderer regressions passed.");
