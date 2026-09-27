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

load("browser-modifiers.js");
load("browser-damage-defense-rules.js");
load("browser-selectable-damage-resistance.js");

function member(id, side, template) {
  return {
    combatant_id: id,
    side,
    state: {
      template,
      opening_buff_id: null,
      active_modifiers: [],
      active_conditional_damage_defenses: [],
      temporary_damage_resistances: [],
      timed_effects: [],
      active_effect_ids: [],
    },
  };
}

const varek = member("varek", "heroes", {
  name: "Varek Ashenmark",
  selectable_damage_resistance: {
    source_id: "fiendish-resilience",
    source_name: "Fiendish Resilience",
    allowed_damage_types: [
      "acid", "bludgeoning", "cold", "fire", "force", "lightning", "necrotic",
      "piercing", "poison", "psychic", "radiant", "slashing", "thunder",
    ],
    forbidden_source_qualifiers: ["magical", "silvered"],
    priority: 90,
  },
  conditional_damage_defenses: [],
  damage_resistances: [],
  damage_immunities: [],
  damage_vulnerabilities: [],
});

const enemy = member("enemy", "monsters", {
  name: "Hammerer",
  attacks: [{
    id: "maul",
    weaponId: "maul",
    name: "Maul",
    kind: "melee",
    diceCount: 2,
    diceSize: 6,
    damageBonus: 4,
    damageType: "bludgeoning",
    damageSourceQualifiers: [],
    onHitDamage: [],
  }],
  saving_throw_actions: [],
  spell_save_actions: [],
  spell_attack_actions: [],
});

const setup = { heroes: [varek], monsters: [enemy] };
const R = window.IRON_PIT_BROWSER_SELECTABLE_DAMAGE_RESISTANCE;
const D = window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES;

assert.equal(R.choose(varek, setup), "bludgeoning");
const event = R.resolve(1, varek, setup);
assert.equal(event.feature_id, "fiendish-resilience");
assert.match(event.description, /bludgeoning resistance/);
assert.equal(varek.state.opening_buff_id, "fiendish-resilience");
assert.deepEqual(varek.state.active_conditional_damage_defenses[0].damageTypes, ["bludgeoning"]);

const ordinary = ["attack", "weapon", "melee"];
assert.equal(D.adjustedDamage(varek.state, 10, "bludgeoning", true, ordinary), 5);
assert.equal(D.adjustedDamage(varek.state, 10, "bludgeoning", true, [...ordinary, "magical"]), 10);
assert.equal(D.adjustedDamage(varek.state, 10, "bludgeoning", true, [...ordinary, "silvered"]), 10);

console.log("2014 Fiendish Resilience browser regression passed.");
