"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
global.window = globalThis;

try {
  // Read generator-owned character truth and execute the shared production aura path.
  for (const file of ["browser-heroes.js", "browser-grid-geometry.js", "browser-state.js", "browser-modifier-validation.js", "browser-modifiers.js",
    "browser-condition-immunity.js", "browser-friendly-save-auras.js"]) {
    vm.runInThisContext(fs.readFileSync(`frontend/${file}`, "utf8"), { filename: file });
  }
  const registry = window.IRON_PIT_BROWSER_HEROES;
  const hero = registry["aurelia-brightshield-l12"];
  const previous = registry["aurelia-brightshield-l11"];
  assert.equal(hero.ruleset, "2024");
  assert.equal(hero.name, previous.name);
  assert.equal(hero.ability_scores.charisma, 17);
  assert.equal(hero.ability_scores.strength, 20);
  assert.equal(hero.max_hp, 100);
  assert.equal(hero.resources["lay-on-hands"], 60);
  assert.equal(hero.friendly_saving_throw_aura.flat_bonus, 3);
  assert.equal(hero.attack_action_weapon_buffs[0].attackRollBonus, 3);
  assert.equal(hero.saving_throw_actions[0].dc, 15);
  assert.equal(hero.saving_throw_actions[0].maxTargets, 3);
  assert.equal(hero.healingActions.find(a => a.id === "cure-wounds").healingBonus, 3);
  assert.equal(hero.saving_throw_bonuses.charisma, 7);
  assert.equal(hero.skill_bonuses.persuasion, 7);
  assert.deepEqual(hero.canonical_prepared_spells, previous.canonical_prepared_spells);
  assert.equal(hero.canonical_prepared_spells.length, 10);
  assert.deepEqual(hero.attacks, previous.attacks);

  const stateApi = window.IRON_PIT_BROWSER_STATE;
  const source = { combatant_id: "aurelia", side: "heroes", position_ft: 0,
    state: stateApi.buildState(hero) };
  const ally = { combatant_id: "ally", side: "heroes", position_ft: 5,
    state: stateApi.buildState(registry["kael-stillwater-l1"]) };
  const setup = { heroes: [source, ally], monsters: [] };
  source.state.position = { x: 0, y: 0 };
  ally.state.position = { x: 1, y: 0 };
  const aura = window.IRON_PIT_BROWSER_FRIENDLY_SAVE_AURAS;
  aura.sync(setup);
  assert.equal(ally.state.active_modifiers.find(m => m.kind === "saving-throw-flat").flat_bonus, 3);
  ally.state.position = { x: 3, y: 0 };
  aura.sync(setup);
  assert.equal(ally.state.active_modifiers.some(m => m.kind === "saving-throw-flat"), false);
  ally.state.position = { x: 1, y: 0 };
  source.state.active_effect_ids.push("incapacitated");
  aura.sync(setup);
  assert.equal(ally.state.active_modifiers.some(m => m.kind === "saving-throw-flat"), false);
  const fresh = stateApi.buildState(hero);
  assert.equal(fresh.current_hp, 100);
  assert.equal(fresh.resources["lay-on-hands"], 60);
  assert.deepEqual(fresh.active_effect_ids, []);
  assert.equal(previous.ability_scores.charisma, 15);
  assert.equal(previous.friendly_saving_throw_aura.flat_bonus, 2);
  console.log("2024 Paladin 12 cumulative build and production aura parity passed.");
} catch (error) {
  console.error("2024 Paladin 12 browser parity failed.", error);
  throw error;
}
