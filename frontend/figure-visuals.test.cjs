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

assert.ok(Object.keys(registry).length >= runnable.length, "reviewed figure registry may include blocked monsters but cannot omit runnable monsters");
for (const template of runnable) {
  assert.ok(registry[template.name], `${template.name} needs a reviewed figure profile before becoming runnable`);
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
assert.equal(monster("Giant Shark", "huge").form, "fish");
assert.equal(monster("Giant Shark", "huge").detail, "shark");
assert.equal(monster("Hunter Shark", "large").form, "fish");
assert.equal(monster("Reef Shark").detail, "shark");
assert.equal(monster("Piranha", "tiny").detail, "piranha");
assert.deepEqual({ form: monster("Swarm of Piranhas").form, detail: monster("Swarm of Piranhas").detail }, { form: "swarm", detail: "piranhas" });
assert.equal(monster("Manticore", "large").detail, "manticore");
assert.equal(monster("Pegasus", "large").detail, "pegasus");
assert.equal(monster("Scorpion", "tiny").form, "scorpion");
assert.equal(monster("Skeleton").detail, "skeleton");
assert.equal(monster("Specter").form, "humanoid");
assert.equal(monster("Specter").detail, "specter");
assert.equal(monster("Spider", "tiny").form, "spider");
assert.deepEqual({ form: monster("Swarm of Bats").form, detail: monster("Swarm of Bats").detail }, { form: "swarm", detail: "bats" });
assert.deepEqual({ form: monster("Swarm of Rats").form, detail: monster("Swarm of Rats").detail }, { form: "swarm", detail: "rats" });
assert.deepEqual({ form: monster("Swarm of Crawling Claws").form, detail: monster("Swarm of Crawling Claws").detail }, { form: "swarm", detail: "crawling-claws" });
assert.equal(monster("Wraith").form, "humanoid");
assert.equal(monster("Wraith").detail, "wraith");
assert.equal(monster("Xorn").form, "brute");
assert.equal(monster("Xorn").detail, "xorn");

const xorn = window.IRON_PIT_BROWSER_MONSTERS["srd-xorn"];
assert.ok(xorn, "Xorn must be exported only after canonical certification succeeds");
assert.deepEqual(xorn.attack_action.slots, [
  { attackIds: ["srd-xorn-bite"], saveActionIds: [] },
  { attackIds: ["srd-xorn-claw"], saveActionIds: [] },
  { attackIds: ["srd-xorn-claw"], saveActionIds: [] },
  { attackIds: ["srd-xorn-claw"], saveActionIds: [] },
]);
const xornBite = xorn.attacks.find((attack) => attack.id === "srd-xorn-bite");
const xornClaw = xorn.attacks.find((attack) => attack.id === "srd-xorn-claw");
assert.deepEqual(
  { bonus: xornBite.bonus, diceCount: xornBite.diceCount, diceSize: xornBite.diceSize, damageBonus: xornBite.damageBonus, damageType: xornBite.damageType },
  { bonus: 6, diceCount: 4, diceSize: 6, damageBonus: 3, damageType: "piercing" },
);
assert.deepEqual(
  { bonus: xornClaw.bonus, diceCount: xornClaw.diceCount, diceSize: xornClaw.diceSize, damageBonus: xornClaw.damageBonus, damageType: xornClaw.damageType },
  { bonus: 6, diceCount: 1, diceSize: 10, damageBonus: 3, damageType: "slashing" },
);
assert.deepEqual(xorn.source_trait_names, ["Earth Glide", "Treasure Sense"]);
assert.deepEqual(xorn.source_bonus_action_names, ["Charge"]);

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
