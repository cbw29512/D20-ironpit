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

for (const file of [
  "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-timed-conditions.js", "browser-grapple.js", "browser-modifier-validation.js", "browser-modifiers.js", "browser-state.js",
  "browser-rage.js", "browser-rolls.js", "browser-undead-fortitude.js", "browser-zero-hp.js",
  "browser-attack-outcome.js", "browser-attack.js", "browser-saving-throws.js", "browser-saves.js",
  "browser-spellcasting.js", "browser-spell-modifiers.js", "browser-spell-attack.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const M = window.IRON_PIT_BROWSER_MODIFIERS;
const A = window.IRON_PIT_BROWSER_SPELL_ATTACK;

function member(id, side, position) {
  const template = {
    id: `template-${id}`, name: id, kind: "character", ruleset: "2014", size: "medium",
    armor_class: 10, max_hp: 30, speed_ft: 30,
    movement_modes: { walk_ft: 30, fly_ft: 0, climb_ft: 0, swim_ft: 0, burrow_ft: 0, hover: false },
    saving_throw_bonuses: {}, skill_bonuses: {}, resources: {},
    damage_immunities: [], damage_resistances: [], damage_vulnerabilities: [],
    condition_immunities: [], critical_hit_minimum: 20, traits: [],
  };
  return { combatant_id: id, side, position_ft: position, state: S.buildState(template) };
}

const blast = {
  id: "test-blast", name: "Test Blast", level: 0, actionCost: "action",
  attackKind: "ranged", range: 120, attackBonus: 5,
  damageDiceCount: 1, damageDiceSize: 10, damageBonus: 0, damageType: "force",
  onHitModifierEffects: [], onHitTimedEffects: [],
};

const caster = member("caster", "heroes", 0);
const marked = member("marked", "monsters", 30);
const setup = { heroes: [caster], monsters: [marked] };
M.add(caster.state, {
  id: "caster:marked-rider:marked:0",
  source_id: "caster", source_effect_id: "marked-rider", source_name: "Marked Rider",
  source_is_magical: true, kind: "bonus-damage", flat_bonus: 0,
  minimum_value: 0, dice_count: 1, dice_size: 6, damage_type: "necrotic",
  target_id: "marked", concentration_required: true,
});

const queue = [15, 7, 4];
window.IRON_PIT_DICE = {
  roll: (sides) => {
    const value = queue.shift();
    if (value == null || value < 1 || value > sides) throw new Error(`invalid fixed d${sides}: ${value}`);
    return value;
  },
  rollMany: (count, sides) => Array.from({ length: count }, () => window.IRON_PIT_DICE.roll(sides)),
};

const event = A.resolve(1, 1, caster, marked, blast, setup, "1:caster");
assert.equal(event.hit, true);
assert.deepEqual(event.damage_components.map((part) => part.source), ["Test Blast", "Marked Rider"]);
assert.deepEqual(event.damage_components.map((part) => part.damage_type), ["force", "necrotic"]);
assert.equal(event.damage_roll.total, 11);
assert.equal(marked.state.current_hp, 19);

console.log("Browser spell-attack bonus-damage modifier regression passed.");
