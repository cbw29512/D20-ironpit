"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-replacement-form-compiler.js"), "utf8"),
  { filename: "browser-replacement-form-compiler.js" },
);
const changeShape = window.IRON_PIT_BROWSER_REPLACEMENT_FORM_COMPILER.compileMonsterChangeShapePhysicalOverlay;

const deva = {
  id: "2014-deva-fixture", name: "Deva", kind: "monster", ruleset: "2014",
  creature_type: "Celestial", challenge_rating: "10", armor_class: 17, max_hp: 136,
  speed_ft: 30, movement_modes: { walk_ft: 30, fly_ft: 90 },
  blindsight_ft: 0, truesight_ft: 0,
  ability_scores: {
    strength: 18, dexterity: 18, constitution: 18,
    intelligence: 17, wisdom: 20, charisma: 20,
  },
  saving_throw_bonuses: { wisdom: 9, charisma: 9 },
  damage_resistances: ["radiant"], condition_immunities: ["charmed"], attacks: [{ id: "deva-mace" }],
  source: "2014 SRD Deva",
};
const wolf = {
  id: "2014-wolf", name: "Wolf", kind: "monster", ruleset: "2014",
  creature_type: "Beast", challenge_rating: "1/4", armor_class: 13, max_hp: 11,
  speed_ft: 40, movement_modes: { walk_ft: 40, fly_ft: 0 },
  blindsight_ft: 0, truesight_ft: 0,
  ability_scores: {
    strength: 12, dexterity: 15, constitution: 12,
    intelligence: 3, wisdom: 12, charisma: 6,
  },
  attacks: [{ id: "wolf-bite" }], source: "2014 SRD Wolf",
};

{
  const active = changeShape(deva, {
    ...wolf,
    damage_resistances: ["fire"],
    damage_immunities: ["poison"],
    condition_immunities: ["poisoned"],
  });
  assert.equal(active.id, "2014-deva-fixture--form-2014-wolf");
  assert.equal(active.kind, "monster");
  assert.equal(active.creature_type, "Celestial");
  assert.equal(active.max_hp, 136);
  assert.equal(active.armor_class, 13);
  assert.equal(active.speed_ft, 40);
  assert.deepEqual(active.movement_modes, { walk_ft: 40, fly_ft: 0 });
  assert.equal(active.ability_scores.strength, 12);
  assert.equal(active.ability_scores.dexterity, 15);
  assert.equal(active.ability_scores.constitution, 18);
  assert.equal(active.ability_scores.wisdom, 20);
  assert.deepEqual(active.saving_throw_bonuses, deva.saving_throw_bonuses);
  assert.deepEqual(active.attacks, deva.attacks);
  assert.deepEqual(active.damage_resistances, ["radiant", "fire"]);
  assert.deepEqual(active.damage_immunities, ["poison"]);
  assert.deepEqual(active.condition_immunities, ["charmed", "poisoned"]);
  assert.deepEqual(deva.damage_resistances, ["radiant"], "Original defenses remain untouched");
  assert.equal(deva.ability_scores.strength, 18, "source must remain immutable");
  assert.equal(deva.armor_class, 17);
}
assert.throws(() => changeShape({ ...deva, kind: "character" }, wolf), /two monster/);
assert.throws(() => changeShape(deva, { ...wolf, ruleset: "2024" }), /ruleset/);
assert.throws(() => changeShape(deva, { ...wolf, creature_type: "Celestial" }), /humanoid or beast/);
assert.throws(() => changeShape(deva, { ...wolf, challenge_rating: "11" }), /challenge rating/);
assert.throws(() => changeShape(deva, { ...wolf, challenge_rating: "1/0" }), /Invalid form challenge/);
console.log("2014 monster Change Shape physical overlay: source and parity checks passed");

{
  const shortlist = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "data", "monster_2014_change_shape_shortlists.json"), "utf8"));
  assert.equal(shortlist.ruleset, "2014");
  const selection = shortlist.policies.find((policy) => policy.source_monster === "Deva");
  assert.ok(selection && selection.keep_original_form_when_not_beneficial);
  assert.equal(selection.form_template_ids.length, 4, "Curated to four source-valid forms");
  const roster = {};
  window.IRON_PIT_BROWSER_MONSTERS_2014 = roster;
  vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-monsters-2014.js"), "utf8"));
  for (const id of selection.form_template_ids) {
    const form = window.IRON_PIT_BROWSER_MONSTERS_2014[id];
    assert.ok(form, "Only certified 2014 monster forms are allowed: " + id);
    assert.equal(form.kind, "monster");
    assert.equal(form.ruleset, "2014");
    assert.ok(["beast", "humanoid"].includes(form.creature_type));
    assert.ok(Number(form.challenge_rating) <= Number(selection.source_cr));
  }
  assert.ok(window.IRON_PIT_BROWSER_MONSTERS_2014["2014-half-red-dragon-veteran"].damage_resistances.includes("fire"));
  assert.ok(!selection.form_template_ids.includes("2014-werebear"), "Uncertified werebear remains excluded");
}
