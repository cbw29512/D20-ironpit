"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES = {
  resolveDamage: (state, amount, type, allowVulnerability = true, sourceQualifiers = [], ignoreResistance = false) => ({
    applied: window.IRON_PIT_BROWSER_ATTACK?.adjustedDamage
      ? window.IRON_PIT_BROWSER_ATTACK.adjustedDamage(state, amount, type, allowVulnerability, sourceQualifiers, ignoreResistance)
      : amount,
    healed: 0,
    sourceName: null,
  }),
};
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

for (const file of [
  "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-timed-conditions.js", "browser-grapple.js", "browser-modifier-validation.js", "browser-modifiers.js", "browser-state.js",
  "browser-rage.js", "browser-rolls.js", "browser-undead-fortitude.js", "browser-zero-hp.js",
  "browser-attack-outcome.js", "browser-attack.js", "browser-saving-throws.js", "browser-saves.js",
  "browser-spellcasting.js", "browser-spell-modifiers.js", "browser-concentration.js",
  "browser-spell-attack.js", "browser-targeted-concentration-damage.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const TD = window.IRON_PIT_BROWSER_TARGETED_CONCENTRATION_DAMAGE;
const SA = window.IRON_PIT_BROWSER_SPELL_ATTACK;

const hex = {
  id: "hex", name: "Hex", level: 1, actionCost: "bonus_action", range: 90,
  diceCount: 1, diceSize: 6, damageType: "necrotic",
  durationRoundsBySlot: { 1: 600, 3: 4800, 5: 14400 },
  retargetAfterTargetZero: true, priority: 10, animation: "targeted-concentration",
};

const mark = {
  id: "hunters-mark", name: "Hunter's Mark", level: 1, actionCost: "bonus_action", range: 90,
  diceCount: 1, diceSize: 6, damageType: "force",
  durationRoundsBySlot: { 1: 600, 3: 4800, 5: 14400 },
  retargetAfterTargetZero: true,
  freeCastResourceId: "favored-enemy-hunters-mark",
  freeCastResourceCost: 1,
  priority: 20, animation: "targeted-concentration",
};

const blast = {
  id: "eldritch-blast", name: "Eldritch Blast", level: 0, actionCost: "action",
  attackKind: "ranged", range: 120, attackBonus: 5,
  damageDiceCount: 1, damageDiceSize: 10, damageBonus: 0, damageType: "force",
  onHitModifierEffects: [], onHitTimedEffects: [],
};

function member(id, side, position, resources = {}) {
  const template = {
    id: `template-${id}`, name: id, kind: "character", ruleset: "2014", size: "medium",
    level: 1, ability_scores: { strength: 9, dexterity: 15, constitution: 14, intelligence: 11, wisdom: 13, charisma: 16 },
    armor_class: 10, max_hp: 30, speed_ft: 30,
    movement_modes: { walk_ft: 30, fly_ft: 0, climb_ft: 0, swim_ft: 0, burrow_ft: 0, hover: false },
    saving_throw_bonuses: {}, skill_bonuses: {}, resources,
    damage_immunities: [], damage_resistances: [], damage_vulnerabilities: [],
    condition_immunities: [], critical_hit_minimum: 20, traits: [],
    targeted_concentration_damage_actions: side === "heroes" ? [hex] : [],
  };
  return { combatant_id: id, side, position_ft: position, state: S.buildState(template) };
}

const varek = member("varek", "heroes", 0, { "spell-slot-1": 1 });
const first = member("first", "monsters", 30);
const second = member("second", "monsters", 35);
const setup = { heroes: [varek], monsters: [first, second] };
window.IRON_PIT_BROWSER_FORMATION = {
  targetOrder: (_member, currentSetup) => currentSetup.monsters
    .filter((target) => target.state.current_hp > 0 && !target.state.is_dead),
};

const hexEvent = TD.resolve(1, 1, varek, setup, "1:varek");
assert.ok(hexEvent);
assert.equal(hexEvent.feature_id, "hex");
assert.equal(varek.state.resources["spell-slot-1"], 0);
assert.equal(varek.state.bonus_action_available, false);
assert.equal(varek.state.action_available, true);
assert.equal(varek.state.concentration.effect_id, "hex");
assert.equal(varek.state.active_modifiers[0].target_id, "first");

const queue = [15, 7, 4];
window.IRON_PIT_DICE = {
  roll: (sides) => {
    const value = queue.shift();
    if (value == null || value < 1 || value > sides) throw new Error(`invalid fixed d${sides}: ${value}`);
    return value;
  },
  rollMany: (count, sides) => Array.from({ length: count }, () => window.IRON_PIT_DICE.roll(sides)),
};
const blastEvent = SA.resolve(2, 1, varek, first, blast, setup, "1:varek");
assert.equal(blastEvent.hit, true);
assert.equal(blastEvent.damage_roll.total, 11);
assert.deepEqual(blastEvent.damage_components.map((part) => part.source), ["Eldritch Blast", "Hex"]);

first.state.current_hp = 0;
first.state.is_alive = false;
first.state.is_dead = true;
S.beginTurn(varek.state);
const moved = TD.resolve(3, 2, varek, setup, "2:varek");
assert.ok(moved);
assert.match(moved.description, /moves Hex/);
assert.equal(varek.state.resources["spell-slot-1"], 0);
assert.equal(varek.state.concentration.effect_id, "hex");
assert.equal(varek.state.active_modifiers.find((item) => item.source_effect_id === "hex").target_id, "second");


const rowan = member("rowan", "heroes", 0, {
  "favored-enemy-hunters-mark": 2,
  "spell-slot-1": 2,
});
rowan.state.template.ruleset = "2024";
rowan.state.template.targeted_concentration_damage_actions = [mark];
const quarry = member("quarry", "monsters", 20);
const rangerSetup = { heroes: [rowan], monsters: [quarry] };
const marked = TD.resolve(4, 1, rowan, rangerSetup, "1:rowan");
assert.ok(marked);
assert.equal(marked.feature_id, "hunters-mark");
assert.equal(rowan.state.resources["favored-enemy-hunters-mark"], 1);
assert.equal(rowan.state.resources["spell-slot-1"], 2);

console.log("Browser targeted concentration damage regression passed.");
