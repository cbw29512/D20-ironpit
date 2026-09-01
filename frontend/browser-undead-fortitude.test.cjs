"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-state.js", "browser-rolls.js", "browser-undead-fortitude.js", "browser-attack.js", "browser-saves.js",
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
const A = window.IRON_PIT_BROWSER_ATTACK;
const V = window.IRON_PIT_BROWSER_SAVES;
const template = {
  id: "test-zombie", name: "Test Zombie", kind: "monster", size: "medium",
  armor_class: 8, max_hp: 10, speed_ft: 20, traits: ["undead-fortitude"], resources: {},
  damage_immunities: [], damage_resistances: [], damage_vulnerabilities: [], condition_immunities: [],
  saving_throw_bonuses: { strength: 1, dexterity: -2, constitution: 4, intelligence: -4, wisdom: -2, charisma: -3 },
};
const zombie = () => S.buildState(structuredClone(template));

{
  const state = zombie(); queue = [20];
  assert.equal(A.applyDamage(state, 10, false, ["bludgeoning"]), "undead_fortitude");
  assert.equal(state.current_hp, 1); assert.equal(state.is_dead, false); assert.deepEqual(queue, []);
}
{
  const state = zombie(); queue = [1];
  assert.equal(A.applyDamage(state, 10, false, ["bludgeoning"]), "dead");
  assert.equal(state.current_hp, 0); assert.equal(state.is_dead, true); assert.deepEqual(queue, []);
}
{
  const state = zombie(); queue = [];
  assert.equal(A.applyDamage(state, 10, false, ["radiant"]), "dead");
  assert.deepEqual(queue, [], "Radiant damage must bypass Undead Fortitude without a save");
}
{
  const state = zombie(); queue = [];
  assert.equal(A.applyDamage(state, 10, true, ["bludgeoning"]), "dead");
  assert.deepEqual(queue, [], "Critical damage must bypass Undead Fortitude without a save");
}
{
  const state = zombie(); queue = [];
  assert.equal(A.applyDamage(state, 10, false, ["bludgeoning", "radiant"]), "dead");
  assert.deepEqual(queue, [], "Any applied Radiant component must bypass Undead Fortitude");
}
{
  const state = zombie(); state.current_hp = 5; state.temporary_hp = 5; queue = [10];
  assert.equal(A.applyDamage(state, 10, false, ["bludgeoning"]), "dead");
  assert.deepEqual(queue, [], "Undead Fortitude DC uses the full damage taken before Temporary HP absorption");
}
{
  const actor = { combatant_id: "monster-1:caster", side: "monsters", position_ft: 0,
    state: S.buildState({ ...template, id: "caster", name: "Caster", traits: [] }) };
  const target = { combatant_id: "monster-2:zombie", side: "monsters", position_ft: 10, state: zombie() };
  target.state.current_hp = 3;
  const action = { id: "test-blast", name: "Test Blast", saveAbility: "dexterity", dc: 20, range: 30,
    damageDiceCount: 1, damageDiceSize: 6, damageBonus: 0, damageType: "bludgeoning",
    successDamage: "none", animation: "save-effect" };
  queue = [1, 6, 20];
  const event = V.resolveAction(1, 1, actor, target, action, 10);
  assert.equal(event.save_succeeded, false);
  assert.equal(target.state.current_hp, 1); assert.equal(target.state.is_dead, false);
  assert.match(event.description, /Undead Fortitude/); assert.deepEqual(queue, []);
}

console.log("Browser Undead Fortitude matches RAW lethal, Radiant, critical, mixed-damage, Temporary HP, and save-action rules.");
