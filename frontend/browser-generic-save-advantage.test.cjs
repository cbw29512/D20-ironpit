"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-state.js", "browser-modifiers.js", "browser-rolls.js", "browser-saves.js",
  "browser-concentration.js", "browser-undead-fortitude.js", "browser-zero-hp.js", "browser-attack.js",
  "browser-aura.js", "browser-turn.js", "browser-spellcasting.js", "browser-spell-modifiers.js", "browser-spell-attack.js",
]) load(file);

let queue = [];
window.IRON_PIT_DICE = {
  roll: (sides) => {
    if (!queue.length) throw new Error(`Unexpected d${sides} roll.`);
    const value = queue.shift();
    assert.ok(value >= 1 && value <= sides, `${value} must be valid for d${sides}`);
    return value;
  },
  rollMany: (count, sides) => Array.from({ length: count }, () => window.IRON_PIT_DICE.roll(sides)),
};

const S = window.IRON_PIT_BROWSER_STATE;
const V = window.IRON_PIT_BROWSER_SAVES;
const A = window.IRON_PIT_BROWSER_ATTACK;
const AU = window.IRON_PIT_BROWSER_AURA;
const TURN = window.IRON_PIT_BROWSER_TURN;
const C = window.IRON_PIT_BROWSER_CONCENTRATION;
const MOD = window.IRON_PIT_BROWSER_MODIFIERS;
const SPELL = window.IRON_PIT_BROWSER_SPELL_ATTACK;

const template = (id, kind = "character") => ({
  id, name: id, kind, size: "medium", level: kind === "character" ? 1 : null,
  armor_class: 10, max_hp: 10, speed_ft: 30, movement_modes: { walk_ft: 30 },
  initiative_bonus: 0, traits: [], resources: {}, condition_immunities: [],
  damage_immunities: [], damage_resistances: [], damage_vulnerabilities: [],
  saving_throw_bonuses: { strength: 0, dexterity: 0, constitution: 0, intelligence: 0, wisdom: 0, charisma: 0 },
});
const authority = (id, kind = "character") => ({ ...template(id, kind), rollAdvantageAura: {
  name: "Test Authority", radius: 10, grantsAttackRollAdvantage: true,
  grantsSavingThrowAdvantage: true, disabledWhileIncapacitated: true,
} });
const member = (id, side, position, t) => ({ combatant_id: id, side, position_ft: position, state: S.buildState(t) });

const source = member("hero-source", "heroes", 0, authority("source"));
const attacker = member("hero-attacker", "heroes", 10, template("attacker"));
const ally = member("hero-ally", "heroes", 10, template("ally"));
const enemy = member("monster-target", "monsters", 15, template("enemy", "monster"));
let setup = { heroes: [source, attacker, ally], monsters: [enemy] };

assert.equal(AU.rollAdvantageSources(source, setup, "attack_roll"), 1, "source benefits from its own aura");
assert.equal(AU.rollAdvantageSources(ally, setup, "saving_throw"), 1);
assert.equal(AU.rollAdvantageSources(enemy, setup, "saving_throw"), 0, "enemy never benefits");
ally.position_ft = 11;
assert.equal(AU.rollAdvantageSources(ally, setup, "saving_throw"), 0, "range is exact");
ally.position_ft = 10;
source.state.active_effect_ids.push("incapacitated");
assert.equal(AU.rollAdvantageSources(ally, setup, "saving_throw"), 0, "Incapacitated source is suppressed");
source.state.active_effect_ids = [];

queue = [2, 18];
let event = V.resolveAction(1, 1, enemy, ally, {
  id: "test-save", name: "Test Save", saveAbility: "wisdom", dc: 15, range: 30,
}, 5, { spendAction: false, spendResource: false, setup });
assert.equal(event.saving_throw_roll.mode, "advantage");
assert.equal(event.saving_throw_roll.selected_roll, 18);
assert.equal(event.save_succeeded, true);

ally.state.active_effect_ids.push("restrained");
queue = [11];
event = V.resolveAction(2, 1, enemy, ally, {
  id: "test-dex", name: "Test Dex", saveAbility: "dexterity", dc: 10, range: 30,
}, 5, { spendAction: false, spendResource: false, setup });
assert.equal(event.saving_throw_roll.mode, "normal", "Advantage and Disadvantage cancel");
ally.state.active_effect_ids = [];

queue = [2, 18, 4];
const attack = A.resolveAttack(3, 1, attacker, enemy, {
  id: "test-sword", name: "Test Sword", kind: "melee", bonus: 0,
  diceCount: 1, diceSize: 4, damageBonus: 0, damageType: "slashing", reach: 5,
}, 5, { spendAction: false, setup });
assert.equal(attack.attack_roll.mode, "advantage");
assert.equal(attack.attack_roll.selected_roll, 18);

const caster = member("hero-caster", "heroes", 10, template("caster"));
const spellTarget = member("monster-spell-target", "monsters", 30, template("spell-target", "monster"));
setup = { heroes: [source, caster], monsters: [spellTarget] };
queue = [3, 17, 4];
const spell = SPELL.resolve(4, 1, caster, spellTarget, {
  id: "test-bolt", name: "Test Bolt", level: 0, actionCost: "action", attackKind: "ranged",
  attackBonus: 0, range: 60, damageDiceCount: 1, damageDiceSize: 4, damageBonus: 0, damageType: "fire",
}, setup, "1:hero-caster");
assert.equal(spell.attack_roll.mode, "advantage");
assert.equal(spell.attack_roll.selected_roll, 17);

const concentrating = member("hero-concentrating", "heroes", 10, template("concentrating"));
setup = { heroes: [source, concentrating], monsters: [] };
C.start(concentrating.state, concentrating.combatant_id, "test-concentration", 1, [source.state, concentrating.state]);
queue = [2, 18];
A.applyDamage(concentrating.state, 1, false, [], [source.state, concentrating.state], AU.rollAdvantageSources(concentrating, setup, "saving_throw"));
assert.ok(concentrating.state.concentration, "Concentration uses the same Advantage source");

const zombieSource = member("monster-source", "monsters", 0, authority("monster-source", "monster"));
const zombieTemplate = { ...template("zombie", "monster"), traits: ["undead-fortitude"] };
const zombie = member("monster-zombie", "monsters", 10, zombieTemplate);
setup = { heroes: [], monsters: [zombieSource, zombie] };
queue = [2, 20];
assert.equal(A.applyDamage(zombie.state, 10, false, ["bludgeoning"], [zombieSource.state, zombie.state], AU.rollAdvantageSources(zombie, setup, "saving_throw")), "undead_fortitude");
assert.equal(zombie.state.current_hp, 1);

const downed = member("hero-downed", "heroes", 10, template("downed"));
downed.state.current_hp = 0; downed.state.is_unconscious = true;
setup = { heroes: [source, downed], monsters: [] };
queue = [1, 12];
event = TURN.deathSave(5, 1, downed, AU.rollAdvantageSources(downed, setup, "saving_throw"));
assert.equal(event.death_save_roll.mode, "advantage");
assert.equal(event.death_save_roll.selected_roll, 12);
assert.equal(downed.state.death_save_successes, 1);
assert.equal(downed.state.death_save_failures, 0, "discarded natural 1 is not a failure");

const blessed = member("hero-blessed", "heroes", 30, template("blessed"));
blessed.state.current_hp = 0; blessed.state.is_unconscious = true;
MOD.add(blessed.state, {
  id: "bless-death", source_id: "hero-source", source_effect_id: "bless",
  kind: "saving-throw-bonus-die", dice_count: 1, dice_size: 4,
});
queue = [8, 2];
event = TURN.deathSave(6, 1, blessed);
assert.equal(event.death_save_roll.selected_roll, 8);
assert.equal(event.death_save_roll.total, 10);
assert.equal(blessed.state.death_save_successes, 1, "saving-throw bonus dice apply to Death Saving Throws");

assert.deepEqual(queue, []);
console.log("Browser generic Advantage sources cover attacks, saves, damage-triggered saves, and Death Saving Throws.");
