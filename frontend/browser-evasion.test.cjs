"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-state.js", "browser-rolls.js", "browser-undead-fortitude.js", "browser-zero-hp.js", "browser-attack.js", "browser-saves.js",
]) load(file);

window.IRON_PIT_DICE = {
  roll: (sides) => { throw new Error(`Unexpected d${sides} roll.`); },
  rollMany: (count, sides) => Array.from({ length: count }, () => window.IRON_PIT_DICE.roll(sides)),
};

const S = window.IRON_PIT_BROWSER_STATE;
const V = window.IRON_PIT_BROWSER_SAVES;
const base = {
  id: "evasion-target", name: "Evasion Target", kind: "monster", ruleset: "2014", size: "medium",
  armor_class: 15, max_hp: 30, speed_ft: 30, traits: ["evasion"], resources: {},
  damage_immunities: [], damage_resistances: [], damage_vulnerabilities: [], condition_immunities: [],
  saving_throw_bonuses: { strength: 0, dexterity: 5, constitution: 0, intelligence: 0, wisdom: 0, charisma: 0 },
};
const member = (id, side, ruleset = "2014", evasion = true) => ({
  combatant_id: id, side, position_ft: 0,
  state: S.buildState({ ...structuredClone(base), id, name: id, ruleset, traits: evasion ? ["evasion"] : [] }),
});
const action = {
  id: "test-blast", name: "Test Blast", saveAbility: "dexterity", dc: 15, range: 30,
  damageDiceCount: 2, damageDiceSize: 6, damageBonus: 0, damageType: "fire",
  successDamage: "half", animation: "save-effect",
};
const run = (target, succeeded, override = {}) => V.resolveAction(
  1, 1, member("caster", "monsters", "2014", false), target, { ...action, ...override }, 0,
  { spendAction: false, checkResource: false, spendResource: false, sharedDamageRolls: [6, 5],
    precomputedSave: { roll: null, succeeded, legendaryResistanceUsed: false } },
);

{
  const target = member("assassin-success", "heroes");
  const event = run(target, true);
  assert.equal(target.state.current_hp, 30);
  assert.equal(event.damage_roll.total, 0);
  assert.deepEqual(event.damage_components[0].rolls, [6, 5]);
  assert.match(event.description, /Evasion/);
}
{
  const target = member("assassin-failure", "heroes");
  const event = run(target, false);
  assert.equal(target.state.current_hp, 25);
  assert.equal(event.damage_roll.total, 5);
}
{
  const target = member("rogue-incapacitated", "heroes", "2024");
  target.state.active_effect_ids.push("incapacitated");
  const event = run(target, false);
  assert.equal(target.state.current_hp, 19);
  assert.equal(event.damage_roll.total, 11);
  assert.doesNotMatch(event.description, /Evasion/);
}
{
  const target = member("wrong-save", "heroes");
  const event = run(target, true, { saveAbility: "constitution" });
  assert.equal(target.state.current_hp, 25);
  assert.equal(event.damage_roll.total, 5);
}

console.log("Browser Evasion shares 2014 monster and 2024 character save-damage rules.");
