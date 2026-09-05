"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
for (const file of ["figure-profiles.js", "figure-visuals.js", "browser-monsters-generated.js"]) {
  vm.runInThisContext(fs.readFileSync(path.join(__dirname, file), "utf8"), { filename: file });
}
const V = window.IRON_PIT_FIGURE_VISUALS;
const registry = window.IRON_PIT_MONSTER_FIGURE_PROFILES;
const runnable = Object.values(window.IRON_PIT_BROWSER_MONSTERS);
const monster = (name, size = "medium") => V.profile({ name, size, kind: "monster", attacks: [{ name: "Bite" }] });

for (const template of runnable) {
  const info = V.profile(template);
  assert.equal(info.certified, true, `${template.name} needs a reviewed or source-backed figure profile`);
  assert.notEqual(info.form, "unknown", `${template.name} must not render as an unknown creature`);
}
for (const name of Object.keys(registry)) {
  const info = monster(name);
  assert.equal(info.certified, true, `${name} must use a reviewed figure profile`);
  assert.notEqual(info.form, "unknown", `${name} must not render as an unknown creature`);
}
assert.ok(registry.Jackal, "Jackal must retain its reviewed canine figure profile");

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
assert.equal(monster("Hippogriff", "large").form, "hippogriff");
assert.equal(monster("Tyrannosaurus Rex", "huge").form, "theropod");
assert.equal(monster("Tyrannosaurus Rex", "huge").detail, "tyrannosaurus");
assert.equal(monster("Kobold Warrior", "small").detail, "kobold");
assert.equal(monster("Hobgoblin Warrior").detail, "hobgoblin");
assert.equal(monster("Giant Wolf Spider").form, "spider");
assert.equal(monster("Giant Wasp").form, "winged-insect");
assert.equal(monster("Giant Centipede").form, "centipede");
assert.equal(monster("Rhinoceros", "large").detail, "horn");
assert.equal(monster("Giant Goat", "large").detail, "horns");
assert.equal(monster("Saber-Toothed Tiger", "large").detail, "sabertooth");

assert.equal(monster("Animated Flying Sword").form, "weapon");
assert.equal(monster("Animated Flying Sword").detail, "flying-sword");
assert.equal(monster("Animated Armor").detail, "animated-armor");
assert.equal(monster("Flying Snake", "tiny").detail, "flying-snake");
assert.equal(monster("Hippopotamus", "large").detail, "hippopotamus");
assert.equal(monster("Killer Whale", "huge").form, "aquatic-mammal");
assert.equal(monster("Killer Whale", "huge").detail, "orca");
assert.equal(monster("Manticore", "large").detail, "manticore");
assert.equal(monster("Pegasus", "large").detail, "pegasus");
assert.equal(monster("Scorpion", "tiny").form, "scorpion");
assert.equal(monster("Skeleton").detail, "skeleton");
assert.equal(monster("Spider", "tiny").form, "spider");
assert.deepEqual({ form: monster("Swarm of Bats").form, detail: monster("Swarm of Bats").detail }, { form: "swarm", detail: "bats" });
assert.deepEqual({ form: monster("Swarm of Rats").form, detail: monster("Swarm of Rats").detail }, { form: "swarm", detail: "rats" });
assert.deepEqual({ form: monster("Swarm of Crawling Claws").form, detail: monster("Swarm of Crawling Claws").detail }, { form: "swarm", detail: "crawling-claws" });

const sourceDragon = V.profile({
  name: "Future Source Dragon", kind: "monster", size: "large", creature_type: "Dragon (Chromatic)",
  visual: { body_style: "dragon", main_hand: "rend" }, attacks: [{ name: "Rend" }],
});
assert.equal(sourceDragon.certified, true);
assert.deepEqual({ form: sourceDragon.form, detail: sourceDragon.detail }, { form: "reptile", detail: "dragon" });
const sourceFiend = V.profile({
  name: "Future Source Fiend", kind: "monster", size: "medium", creature_type: "Fiend",
  visual: { body_style: "monster", main_hand: "claw" }, attacks: [{ name: "Claw" }],
});
assert.equal(sourceFiend.certified, true);
assert.equal(sourceFiend.form, "brute");

const unknown = monster("Future Unreviewed Monster");
assert.equal(unknown.certified, false);
assert.equal(unknown.form, "unknown", "monsters without reviewed or source identity must still fail visually closed");

const hero = V.profile({
  name: "Audited Guardian", kind: "character", size: "medium", archetype: "Paladin",
  visual: { figure_form: "humanoid", main_hand: "longsword", off_hand: "shield", role: "paladin" }, attacks: [],
});
assert.equal(hero.certified, true);
assert.equal(hero.weapon, "longsword");
assert.equal(hero.offHand, "shield");
assert.equal(hero.role, "paladin");

console.log("Reviewed and source-backed monster figure identity regressions passed.");
