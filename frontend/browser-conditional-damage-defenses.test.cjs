"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

load("browser-modifier-validation.js");
load("browser-modifiers.js");
load("browser-damage-defense-rules.js");
load("browser-monsters-2014.js");
load("browser-heroes.js");

const D = window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES;
const ordinary = ["attack", "weapon", "melee"];
const member = (template) => ({
  template,
  active_conditional_damage_defenses: [],
  temporary_damage_resistances: [],
  timed_effects: [],
  zone_damage_immunities: [],
  active_effect_ids: [],
});

const gargoyle = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-gargoyle"];
assert.ok(gargoyle, "2014 Gargoyle must unlock in the certified browser roster");
assert.equal(gargoyle.conditional_damage_defenses.length, 1);
assert.equal(gargoyle.conditional_damage_defenses[0].kind, "resistance");
assert.deepEqual(gargoyle.conditional_damage_defenses[0].requiredSourceQualifiers, ["attack"]);
assert.deepEqual(
  gargoyle.conditional_damage_defenses[0].forbiddenSourceQualifiers.sort(),
  ["adamantine", "magical"],
);

const gargoyleState = member(gargoyle);
assert.equal(D.adjustedDamage(gargoyleState, 10, "slashing", true, ordinary), 5);
assert.equal(D.adjustedDamage(gargoyleState, 10, "slashing", true, [...ordinary, "adamantine"]), 10);
assert.equal(D.adjustedDamage(gargoyleState, 10, "slashing", true, [...ordinary, "magical"]), 10);
assert.equal(D.adjustedDamage(gargoyleState, 10, "slashing", true, ["weapon", "melee"]), 10);

const werewolf = member({
  damage_resistances: [],
  damage_immunities: [],
  damage_vulnerabilities: [],
  conditional_damage_defenses: [{
    id: "test-werewolf",
    kind: "immunity",
    damageTypes: ["bludgeoning", "piercing", "slashing"],
    requiredSourceQualifiers: ["attack"],
    forbiddenSourceQualifiers: ["magical", "silvered"],
  }],
});
assert.equal(D.adjustedDamage(werewolf, 10, "piercing", true, ordinary), 0);
assert.equal(D.adjustedDamage(werewolf, 10, "piercing", true, [...ordinary, "silvered"]), 10);
assert.equal(D.adjustedDamage(werewolf, 10, "piercing", true, [...ordinary, "magical"]), 10);

const manufacturedQualifiers = (hero) => (hero.attacks || [])
  .filter((attack) => attack.weaponId !== "unarmed-strike" && String(attack.name || "").toLowerCase() !== "unarmed strike")
  .map((attack) => attack.damageSourceQualifiers || []);
const karnok1 = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-2014-l1"];
const karnok3 = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-2014-l3"];
const karnok5 = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-2014-l5"];
assert.ok(karnok1 && karnok3 && karnok5, "2014 Karnok loadout snapshots must exist");
assert.ok(manufacturedQualifiers(karnok1).every((item) => !item.includes("silvered") && !item.includes("magical")));
assert.ok(manufacturedQualifiers(karnok3).every((item) => item.includes("silvered")));
assert.ok(manufacturedQualifiers(karnok5).every((item) => item.includes("magical")));

console.log("2014 conditional damage-defense browser regression passed.");
