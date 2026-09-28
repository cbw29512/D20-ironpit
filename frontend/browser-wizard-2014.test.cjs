"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
);

window.IRON_PIT_BROWSER_SPELLCASTING = {
  legalSlotLevels: () => [],
};
window.IRON_PIT_DICE = {
  rollMany: (count) => Array(count).fill(1),
};
window.IRON_PIT_BROWSER_ATTACK = {
  applyDamage: (state, amount) => {
    state.current_hp = Math.max(0, state.current_hp - amount);
    return "damaged";
  },
};

load("browser-spell-features.js");
const F = window.IRON_PIT_BROWSER_SPELL_FEATURES;

const state = {
  current_hp: 100,
  temporary_hp: 0,
  resources: {
    "signature-spell-fireball": 1,
    "signature-spell-lightning-bolt": 1,
  },
  feature_use_counts: {},
  template: {
    spell_specific_cast_grants: [
      {
        source_id: "spell-mastery-burning-hands",
        source_name: "Spell Mastery",
        spell_id: "burning-hands",
        slot_level: 1,
        unlimited: true,
        resource_id: null,
        resource_cost: 1,
      },
      {
        source_id: "signature-spell-fireball",
        source_name: "Signature Spells",
        spell_id: "fireball",
        slot_level: 3,
        unlimited: false,
        resource_id: "signature-spell-fireball",
        resource_cost: 1,
      },
      {
        source_id: "signature-spell-lightning-bolt",
        source_name: "Signature Spells",
        spell_id: "lightning-bolt",
        slot_level: 3,
        unlimited: false,
        resource_id: "signature-spell-lightning-bolt",
        resource_cost: 1,
      },
    ],
    spell_damage_maximizer: {
      source_id: "overchannel",
      source_name: "Overchannel",
      minimum_spell_level: 1,
      maximum_spell_level: 5,
      free_uses: 1,
      self_damage_die_size: 12,
      repeat_base_dice_per_spell_level: 2,
      repeat_increment_dice_per_spell_level: 1,
      self_damage_type: "necrotic",
      bypasses_resistance_and_immunity: true,
    },
  },
};
const caster = { combatant_id: "elian", state };
const setup = { heroes: [caster], monsters: [] };

const burning = { id: "burning-hands", level: 1, damageDiceCount: 3, damageDiceSize: 6 };
assert.deepEqual(F.legalSaveSpellLevels(state, "turn", burning), [1]);

const fireball = { id: "fireball", level: 3, damageDiceCount: 8, damageDiceSize: 6 };
const spent = F.spendGrant(state, fireball, 3);
assert.equal(spent.grant.source_name, "Signature Spells");
assert.equal(spent.remaining, 0);
assert.equal(state.resources["signature-spell-lightning-bolt"], 1);

assert.equal(F.shouldAutoMaximize(state, fireball), true);
assert.deepEqual(F.maximizedRolls(fireball), Array(8).fill(6));
assert.equal(F.applyMaximizerCost(caster, fireball, setup), null);
assert.equal(state.current_hp, 100);

const repeat = F.applyMaximizerCost(caster, fireball, setup);
assert.equal(repeat.count, 6);
assert.equal(repeat.total, 6);
assert.equal(state.current_hp, 94);
assert.equal(state.feature_use_counts.overchannel, 2);

console.log("browser 2014 Wizard spell feature regressions passed");
