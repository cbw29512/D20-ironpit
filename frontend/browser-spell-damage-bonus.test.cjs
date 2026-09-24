const assert = require("assert");
const fs = require("fs");
const vm = require("vm");

global.window = global;
vm.runInThisContext(fs.readFileSync("frontend/browser-spell-damage-bonus.js", "utf8"));

const nyra = {
  template: {
    name: "Nyra Emberveil",
    ability_scores: { charisma: 18 },
    spell_damage_bonus_grants: [{
      source_id: "elemental-affinity",
      source_name: "Elemental Affinity",
      ability: "charisma",
      eligible_spell_ids: [],
      eligible_damage_types: ["fire"],
    }],
  },
};
assert.equal(window.IRON_PIT_BROWSER_SPELL_DAMAGE_BONUS.matches(nyra, "fireball", "fire").total, 4);
assert.equal(window.IRON_PIT_BROWSER_SPELL_DAMAGE_BONUS.matches(nyra, "disintegrate", "force").total, 0);

const elian = {
  template: {
    name: "Elian Starweaver",
    ability_scores: { intelligence: 20 },
    spell_damage_bonus_grants: [{
      source_id: "empowered-evocation",
      source_name: "Empowered Evocation",
      ability: "intelligence",
      eligible_spell_ids: ["fire-bolt", "fireball"],
      eligible_damage_types: [],
    }],
  },
};
assert.equal(window.IRON_PIT_BROWSER_SPELL_DAMAGE_BONUS.matches(elian, "fire-bolt", "fire").total, 5);
assert.equal(window.IRON_PIT_BROWSER_SPELL_DAMAGE_BONUS.matches(elian, "fireball", "fire").total, 5);
assert.equal(window.IRON_PIT_BROWSER_SPELL_DAMAGE_BONUS.matches(elian, "disintegrate", "force").total, 0);

console.log("Browser generic spell damage bonus passed.");
