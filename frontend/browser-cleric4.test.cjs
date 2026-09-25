"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-modifiers.js", "browser-state.js", "browser-rolls.js", "browser-zero-hp.js", "browser-ability-hooks.js", "browser-attack-outcome.js", "browser-attack.js",
  "browser-saves.js", "browser-concentration.js", "browser-spell-modifiers.js", "browser-spellcasting.js",
  "browser-spell-area.js", "browser-offense-value.js", "browser-spell-policy.js", "browser-spell-resolution.js",
  "browser-spell-attack-policy.js", "browser-spell-attack.js", "browser-spell-offense.js", "browser-precombat-spells.js",
]) load(file);

const H = window.IRON_PIT_BROWSER_HEROES;
const S = window.IRON_PIT_BROWSER_STATE;
const P = window.IRON_PIT_BROWSER_PRECOMBAT_SPELLS;
const O = window.IRON_PIT_BROWSER_SPELL_OFFENSE;

const level7 = H["seraphine-dawnshield-l7"];
const level8 = H["seraphine-dawnshield-l8"];
assert.ok(level7, "Seraphine Cleric 7 must exist in generated browser heroes.");
assert.ok(level8, "Seraphine Cleric 8 must exist in generated browser heroes.");

const sacred7 = level7.spell_save_actions.find((spell) => spell.id === "sacred-flame");
const sacred8 = level8.spell_save_actions.find((spell) => spell.id === "sacred-flame");
assert.equal(level7.level, 7);
assert.equal(level7.max_hp, 38);
assert.equal(level7.ability_scores.wisdom, 19);
assert.equal(level7.resources["spell-slot-4"], 1);
assert.equal(sacred7.damageDiceCount, 2);
assert.equal(sacred7.damageDiceSize, 8);
assert.equal(sacred7.damageBonus, 4);
assert.equal(sacred7.dc, 15);
assert.equal(level7.spell_attack_actions[0].attackBonus, 7);
assert.equal(level7.canonical_prepared_spells.at(-1).id, "prayer-of-healing");
assert.deepEqual(level7.canonical_always_prepared_spells.slice(-2).map((spell) => spell.id), [
  "aura-of-life", "death-ward",
]);

assert.equal(level8.level, 8);
assert.equal(level8.max_hp, 43);
assert.equal(level8.ability_scores.wisdom, 20);
assert.equal(level8.ability_scores.charisma, 15);
assert.equal(level8.resources["spell-slot-4"], 2);
assert.equal(sacred8.damageDiceCount, 2);
assert.equal(sacred8.damageDiceSize, 8);
assert.equal(sacred8.damageBonus, 5);
assert.equal(sacred8.dc, 16);
assert.equal(level8.spell_attack_actions[0].attackBonus, 8);
assert.deepEqual(level8.canonical_prepared_spells.slice(-2).map((spell) => spell.id), [
  "prayer-of-healing", "guardian-of-faith",
]);

const cleric = H["seraphine-dawnshield-l4"];
assert.ok(cleric, "Seraphine Cleric 4 must exist in generated browser heroes.");

assert.equal(cleric.level, 4);
assert.equal(cleric.armor_class, 15);
assert.equal(cleric.max_hp, 23);
assert.equal(cleric.saving_throw_bonuses.wisdom, 6);
assert.equal(cleric.skill_bonuses.medicine, 6);
assert.deepEqual(cleric.resources, {
  "adrenaline-rush": 2,
  "channel-divinity": 2,
  "relentless-endurance": 1,
  "spell-slot-1": 4,
  "spell-slot-2": 3,
});
assert.deepEqual(cleric.canonical_cantrips.map((spell) => spell.id), [
  "sacred-flame", "light", "thaumaturgy", "mending",
]);
assert.deepEqual(cleric.canonical_prepared_spells.map((spell) => spell.id), [
  "guiding-bolt", "shield-of-faith", "healing-word", "detect-magic",
  "create-or-destroy-water", "augury", "inflict-wounds",
]);
assert.deepEqual(cleric.spell_save_actions.map((spell) => spell.id), ["sacred-flame", "inflict-wounds"]);
const inflict = cleric.spell_save_actions[1];
assert.equal(inflict.level, 1);
assert.equal(inflict.range, 5);
assert.equal(inflict.saveAbility, "constitution");
assert.equal(inflict.dc, 14);
assert.equal(inflict.damageDiceCount, 2);
assert.equal(inflict.damageDiceSize, 10);
assert.equal(inflict.damageType, "necrotic");
assert.equal(inflict.successDamage, "half");
assert.equal(cleric.spell_attack_actions[0].attackBonus, 6);
assert.deepEqual(cleric.healingActions.map((spell) => spell.healingBonus), [7, 7]);

function member(template, id, side, position) {
  return { combatant_id: id, side, position_ft: position, state: S.buildState(structuredClone(template)) };
}

const caster = member(cleric, "cleric", "heroes", 5);
const target = member(H["karnok-stoneward-l1"], "fighter", "monsters", 10);
const setup = { heroes: [caster], monsters: [target] };

const prep = P.prepare(setup, 1);
assert.equal(prep.events.length, 1);
assert.equal(prep.events[0].feature_id, "aid");
assert.equal(caster.state.opening_buff_spell_id, "aid");
assert.equal(caster.state.resources["spell-slot-2"], 2);
assert.equal(caster.state.concentration, null, "Aid is the single opening buff and does not require Concentration.");

caster.state.resources["spell-slot-2"] = 3;
const forbiddenRebuff = P.prepare(setup, 1);
assert.equal(forbiddenRebuff.events.length, 0, "A caster may never cast a second opening buff in the same battle.");
assert.equal(caster.state.resources["spell-slot-2"], 3);

S.beginTurn(caster.state);
const rolls = [1, 10, 9, 8];
window.IRON_PIT_DICE = {
  roll: (sides) => {
    assert.ok(rolls.length, `fixed dice exhausted before d${sides}`);
    const value = rolls.shift();
    assert.ok(value >= 1 && value <= sides, `${value} is invalid for d${sides}`);
    return value;
  },
  rollMany: (count, sides) => Array.from({ length: count }, () => window.IRON_PIT_DICE.roll(sides)),
};
const offense = O.resolve(1, 1, caster, setup, "1:cleric");
assert.equal(offense.sequence, 3);
assert.equal(offense.events[0].feature_id, "inflict-wounds");
assert.equal(offense.events[1].feature_id, "inflict-wounds");
assert.equal(offense.events[1].save_succeeded, false);
assert.equal(offense.events[1].damage_roll.total, 27);
assert.equal(caster.state.resources["spell-slot-1"], 4);
assert.equal(caster.state.resources["spell-slot-2"], 2);
assert.equal(rolls.length, 0, "Inflict Wounds upcast consumes exactly one save d20 plus three damage dice.");

console.log("Generated Browser Cleric 4 ASI, one-opening-buff, and Inflict Wounds regressions passed.");
