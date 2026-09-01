"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-condition-rules.js", "browser-action-economy.js", "browser-modifiers.js",
  "browser-state.js", "browser-concentration.js", "browser-spell-modifiers.js", "browser-precombat-spells.js",
  "browser-spellcasting.js", "browser-spell-area.js", "browser-spell-policy.js", "browser-spell-attack-policy.js",
]) load(file);

const H = window.IRON_PIT_BROWSER_HEROES;
const S = window.IRON_PIT_BROWSER_STATE;
const P = window.IRON_PIT_BROWSER_PRECOMBAT_SPELLS;
const A = window.IRON_PIT_BROWSER_SPELL_ATTACK_POLICY;
const V = window.IRON_PIT_BROWSER_SPELL_POLICY;
const cleric = H["seraphine-dawnshield-l1"];
assert.ok(cleric, "Seraphine must exist in generated browser heroes.");

assert.equal(cleric.class_id, "cleric");
assert.equal(cleric.level, 1);
assert.equal(cleric.armor_class, 17);
assert.equal(cleric.max_hp, 10);
assert.equal(cleric.saving_throw_bonuses.wisdom, 5);
assert.equal(cleric.saving_throw_bonuses.charisma, 2);
assert.deepEqual(cleric.resources, {
  "adrenaline-rush": 2,
  "relentless-endurance": 1,
  "spell-slot-1": 2,
});

assert.deepEqual(cleric.healingActions.map((spell) => spell.id), ["cure-wounds"]);
const cure = cleric.healingActions[0];
assert.equal(cure.range, 5);
assert.equal(cure.diceCount, 2);
assert.equal(cure.diceSize, 8);
assert.equal(cure.healingBonus, 3);
assert.equal(cure.resourceId, "spell-slot-1");

assert.deepEqual(cleric.spell_save_actions.map((spell) => spell.id), ["sacred-flame"]);
const flame = cleric.spell_save_actions[0];
assert.equal(flame.level, 0);
assert.equal(flame.range, 60);
assert.equal(flame.saveAbility, "dexterity");
assert.equal(flame.dc, 13);
assert.equal(flame.damageDiceCount, 1);
assert.equal(flame.damageDiceSize, 8);
assert.equal(flame.damageType, "radiant");

assert.deepEqual(cleric.spell_attack_actions.map((spell) => spell.id), ["guiding-bolt"]);
const bolt = cleric.spell_attack_actions[0];
assert.equal(bolt.level, 1);
assert.equal(bolt.range, 120);
assert.equal(bolt.attackBonus, 5);
assert.equal(bolt.damageDiceCount, 4);
assert.equal(bolt.damageDiceSize, 6);
assert.equal(bolt.damageType, "radiant");
assert.equal(bolt.onHitModifierEffects[0].consumeOnAttackAgainst, true);
assert.equal(bolt.onHitModifierEffects[0].expiresAfterSourceTurns, 1);

assert.deepEqual(cleric.defensive_spell_actions.map((spell) => spell.id), ["bless", "shield-of-faith"]);
assert.equal(cleric.defensive_spell_actions[0].targetCount, 3);
assert.equal(cleric.defensive_spell_actions[0].priority, 30);

const caster = { combatant_id: "cleric", side: "heroes", position_ft: 0, state: S.buildState(structuredClone(cleric)) };
const enemyTemplate = structuredClone(H["karnok-stoneward-l1"]);
const enemy = { combatant_id: "enemy", side: "monsters", position_ft: 10, state: S.buildState(enemyTemplate) };
const setup = { heroes: [caster], monsters: [enemy] };

const prep = P.prepare(setup, 1);
assert.equal(prep.events.length, 1);
assert.equal(prep.events[0].feature_id, "bless");
assert.equal(caster.state.resources["spell-slot-1"], 1);

S.beginTurn(caster.state);
const turnKey = "1:cleric";
const attackChoice = A.choose(caster, setup, turnKey);
assert.equal(attackChoice.action.id, "guiding-bolt");

caster.state.resources["spell-slot-1"] = 0;
const noBolt = A.choose(caster, setup, turnKey);
assert.equal(noBolt, null);
const cantrip = V.choose(caster, setup, turnKey);
assert.equal(cantrip.action.id, "sacred-flame");
assert.equal(cantrip.slotLevel, 0);

console.log("Browser Cleric 1 generated package and spell-priority regressions passed.");
