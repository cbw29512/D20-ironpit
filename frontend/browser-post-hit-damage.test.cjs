"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync("frontend/" + name, "utf8"), { filename: name },
);

window.IRON_PIT_DICE = {
  rolls: [],
  roll(sides) {
    if (!this.rolls.length) throw new Error("No queued d" + sides + " roll");
    return this.rolls.shift();
  },
  rollMany(count, sides) {
    return Array.from({ length: count }, () => this.roll(sides));
  },
};

load("browser-action-economy.js");
load("browser-resources.js");
load("browser-spellcasting.js");
load("browser-post-hit-damage.js");
load("browser-rolls.js");

function attacker() {
  return {
    template: {
      name: "Aurelia Brightshield",
      max_hp: 20,
      traits: [],
      unlimited_resources: [],
      resource_backed_post_hit_damage: {
        source_id: "divine-smite-2024",
        source_name: "Divine Smite",
        trigger_attack_ids: ["aurelia-longsword"],
        action_cost: "bonus_action",
        free_resource_id: "paladins-smite-free-cast",
        printed_spell_level: 1,
        max_slot_level: 5,
        base_dice_count: 2,
        dice_per_slot_above: 1,
        dice_size: 8,
        damage_type: "radiant",
        bonus_target_creature_types: ["fiend", "undead"],
        bonus_target_dice_count: 1,
        doubles_on_critical: true,
      },
    },
    current_hp: 20,
    resources: { "paladins-smite-free-cast": 1, "spell-slot-1": 2 },
    action_available: true,
    bonus_action_available: true,
    reaction_available: true,
    is_dead: false,
    is_unconscious: false,
    turn_terminated: false,
    spell_slot_expended_turn_key: null,
    feature_last_turn_keys: { "savage-attacker": "1:aurelia" },
  };
}

const attack = {
  id: "aurelia-longsword",
  name: "Longsword",
  kind: "melee",
  diceCount: 1,
  diceSize: 8,
  damageBonus: 3,
  damageType: "slashing",
  onHitDamage: [],
};
const target = {
  template: { max_hp: 100, creature_type: "Fiend" },
  current_hp: 100,
  is_dead: false,
  is_alive: true,
};

let hero = attacker();
window.IRON_PIT_DICE.rolls = [4, 8, 7, 6];
let result = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(
  hero, attack, false, "normal", "1:aurelia", null, target,
);
assert.deepEqual(result.components.map((part) => part.source), ["Longsword", "Divine Smite"]);
assert.equal(result.components[1].notation, "3d8+0");
assert.equal(result.roll.total, 28);
assert.equal(hero.bonus_action_available, false);
assert.equal(hero.resources["paladins-smite-free-cast"], 0);
assert.equal(hero.resources["spell-slot-1"], 2);

hero = attacker();
hero.resources["paladins-smite-free-cast"] = 0;
window.IRON_PIT_DICE.rolls = [4, 5, 8, 7, 6, 5];
result = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(
  hero, attack, true, "normal", "2:aurelia", null,
  { ...target, template: { max_hp: 100, creature_type: "Humanoid" } },
);
assert.equal(result.components[1].notation, "4d8+0");
assert.deepEqual(result.components[1].rolls, [8, 7, 6, 5]);
assert.equal(hero.resources["spell-slot-1"], 1);
assert.equal(hero.spell_slot_expended_turn_key, "2:aurelia");

console.log("Browser post-hit resource damage regressions passed.");
