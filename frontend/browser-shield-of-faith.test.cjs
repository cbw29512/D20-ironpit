"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-grapple.js", "browser-modifiers.js", "browser-state.js", "browser-rage.js", "browser-rolls.js",
  "browser-undead-fortitude.js", "browser-zero-hp.js", "browser-attack.js", "browser-saves.js",
  "browser-concentration.js", "browser-spell-effects.js", "browser-spell-modifiers.js", "browser-precombat-spells.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const M = window.IRON_PIT_BROWSER_MODIFIERS;
const A = window.IRON_PIT_BROWSER_ATTACK;
const P = window.IRON_PIT_BROWSER_PRECOMBAT_SPELLS;
const shield = window.IRON_PIT_BROWSER_SPELL_EFFECTS["shield-of-faith"];
const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];

function dice(values) {
  const rolls = [...values];
  window.IRON_PIT_DICE = { roll: (sides) => {
    if (!rolls.length) throw new Error("fixed dice exhausted");
    const value = rolls.shift();
    if (value < 1 || value > sides) throw new Error(`invalid d${sides}: ${value}`);
    return value;
  }, rollMany: (count, sides) => Array.from({ length: count }, () => window.IRON_PIT_DICE.roll(sides)) };
}

const casterTemplate = structuredClone(base);
casterTemplate.defensive_spell_actions = [shield];
casterTemplate.resources = { "spell-slot-1": 1 };
const caster = { combatant_id: "caster", side: "heroes", position_ft: 0, state: S.buildState(casterTemplate) };

const attackerTemplate = structuredClone(base);
attackerTemplate.id = "attacker";
attackerTemplate.name = "Attacker";
attackerTemplate.traits = [];
attackerTemplate.resources = {};
const attacker = { combatant_id: "attacker", side: "monsters", position_ft: 5, state: S.buildState(attackerTemplate) };
const setup = { heroes: [caster], monsters: [attacker] };
const attack = { id: "test-blade", name: "Test Blade", kind: "melee", reach: 5, bonus: 4,
  diceCount: 1, diceSize: 4, damageBonus: 0, damageType: "slashing", onHitDamage: [], conditionalDamage: null };

assert.equal(shield.actionCost, "bonus_action");
assert.equal(shield.range, 60);
assert.equal(shield.durationMinutes, 10);
assert.deepEqual(shield.modifierEffects, [{ damageType: null, diceCount: 0, diceSize: 0, flatBonus: 2, kind: "armor-class" }]);

const prep = P.prepare(setup);
assert.equal(prep.events.length, 1);
assert.equal(prep.events[0].feature_id, "shield-of-faith");
assert.equal(caster.state.resources["spell-slot-1"], 0);
assert.equal(caster.state.concentration.effect_id, "shield-of-faith");
assert.equal(M.effectiveArmorClass(caster.state), caster.state.template.armor_class + 2);

// +4 attack: natural 14 totals 18 and misses AC 19 because Shield of Faith is active.
dice([14]);
const miss = A.resolveAttack(2, 1, attacker, caster, attack, 5, { spendAction: false, setup });
assert.equal(miss.hit, false);
assert.equal(caster.state.concentration.effect_id, "shield-of-faith");

// Natural 16 totals 20, deals 1 damage, then the caster rolls 1 on the DC 10 Constitution save and loses Concentration.
dice([16, 1, 1]);
const hit = A.resolveAttack(3, 1, attacker, caster, attack, 5, { spendAction: false, setup });
assert.equal(hit.hit, true);
assert.equal(caster.state.concentration, null);
assert.deepEqual(caster.state.active_modifiers, []);
assert.equal(M.effectiveArmorClass(caster.state), caster.state.template.armor_class);

console.log("Generated Shield of Faith browser lifecycle regression passed.");
