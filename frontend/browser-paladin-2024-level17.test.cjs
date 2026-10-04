"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
global.window = globalThis;

try {
  vm.runInThisContext(
    fs.readFileSync("frontend/browser-heroes.js", "utf8"),
    { filename: "browser-heroes.js" },
  );

  const registry = window.IRON_PIT_BROWSER_HEROES;
  const hero = registry["aurelia-brightshield-l17"];
  const previous = registry["aurelia-brightshield-l16"];
  assert.ok(hero && previous);
  assert.equal(hero.name, previous.name);
  assert.equal(hero.level, 17);
  assert.equal(hero.max_hp, 140);
  assert.equal(hero.resources["lay-on-hands"], 85);
  assert.equal(hero.resources["spell-slot-4"], 3);
  assert.equal(hero.resources["spell-slot-5"], 1);
  const primaryAttack = hero.attacks.find(item => item.id === hero.primary_attack_id);
  assert.ok(primaryAttack);
  assert.equal(primaryAttack.bonus, 11);

  const flameStrike = hero.spell_save_actions.find(item => item.id === "flame-strike");
  assert.ok(flameStrike);
  assert.equal(flameStrike.level, 5);
  assert.equal(flameStrike.dc, 18);
  assert.equal(flameStrike.saveAbility, "dexterity");
  assert.equal(flameStrike.successDamage, "half");
  assert.deepEqual(
    flameStrike.damageComponents.map(part => [
      part.diceCount, part.diceSize, part.damageType,
    ]),
    [[5, 6, "fire"], [5, 6, "radiant"]],
  );

  assert.equal(hero.canonical_prepared_spells.length, 14);
  assert.deepEqual(
    hero.canonical_prepared_spells.slice(-2).map(item => item.id),
    ["destructive-wave", "greater-restoration"],
  );

  console.log("2024 Paladin 17 progression and Flame Strike browser parity passed.");
} catch (error) {
  console.error("2024 Paladin 17 browser parity failed.", error);
  throw error;
}
