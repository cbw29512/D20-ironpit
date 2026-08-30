"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
for (const file of ["figure-profiles.js", "figure-visuals.js"]) {
  vm.runInThisContext(fs.readFileSync(path.join(__dirname, file), "utf8"), { filename: file });
}
const V = window.IRON_PIT_FIGURE_VISUALS;
const registry = window.IRON_PIT_MONSTER_FIGURE_PROFILES;
const monster = (name, size = "medium") => V.profile({ name, size, kind: "monster", attacks: [{ name: "Bite" }] });

assert.equal(Object.keys(registry).length, 63, "every currently RAW-ready monster needs a reviewed figure profile");
for (const name of Object.keys(registry)) {
  const info = monster(name);
  assert.equal(info.certified, true, `${name} must use a reviewed figure profile`);
  assert.notEqual(info.form, "unknown", `${name} must not render as an unknown creature`);
}

assert.deepEqual(
  { form: monster("Owlbear", "large").form, detail: monster("Owlbear", "large").detail },
  { form: "bear", detail: "owlbear" },
);
assert.deepEqual(
  { form: monster("Axe Beak", "large").form, detail: monster("Axe Beak", "large").detail },
  { form: "bird", detail: "beak" },
);
assert.equal(monster("Baboon", "small").form, "primate");
assert.equal(monster("Plesiosaurus", "large").form, "aquatic-reptile");
assert.equal(monster("Pteranodon").form, "pterosaur");
assert.equal(monster("Giant Wolf Spider").form, "spider");
assert.equal(monster("Giant Wasp").form, "winged-insect");
assert.equal(monster("Giant Centipede").form, "centipede");
assert.equal(monster("Rhinoceros", "large").detail, "horn");
assert.equal(monster("Giant Goat", "large").detail, "horns");
assert.equal(monster("Saber-Toothed Tiger", "large").detail, "sabertooth");

const unknown = monster("Future Unreviewed Monster");
assert.equal(unknown.certified, false);
assert.equal(unknown.form, "unknown", "uncertified monsters must fail visually closed rather than guessing anatomy");

const hero = V.profile({
  name: "Audited Guardian", kind: "character", size: "medium", archetype: "Paladin",
  visual: { figure_form: "humanoid", main_hand: "longsword", off_hand: "shield", role: "paladin" }, attacks: [],
});
assert.equal(hero.certified, true);
assert.equal(hero.weapon, "longsword");
assert.equal(hero.offHand, "shield");
assert.equal(hero.role, "paladin");

console.log("Reviewed monster and hero figure identity regressions passed.");
