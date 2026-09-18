"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

load("browser-rolls.js");
load("browser-condition-rules.js");
load("browser-modifiers.js");
load("browser-state.js");
load("browser-defensive-modifier-rules.js");
load("browser-condition-immunity.js");
load("browser-saves.js");
load("browser-2014-paladin-auras.js");

const M = window.IRON_PIT_BROWSER_MODIFIERS;
const S = window.IRON_PIT_BROWSER_STATE;
const I = window.IRON_PIT_BROWSER_CONDITION_IMMUNITY;
const A = window.IRON_PIT_BROWSER_PALADIN_AURAS_2014;

function template(name, extra = {}) {
  return {
    id: name.toLowerCase(), name, kind: "character", ruleset: "2014", size: "medium",
    max_hp: 20, speed_ft: 30, condition_immunities: [], traits: [], resources: {},
    saving_throw_bonuses: { strength: 0, dexterity: 0, constitution: 0, intelligence: 0, wisdom: 2, charisma: 0 },
    ...extra,
  };
}

function member(id, side, position, tpl) {
  return { combatant_id: id, side, position_ft: position, state: S.buildState(tpl) };
}

function setup(sourceTemplate, targetPosition = 5) {
  const source = member("aurelia", "heroes", 0, sourceTemplate);
  const ally = member("ally", "heroes", targetPosition, template("Ally"));
  const enemy = member("enemy", "monsters", 30, template("Enemy", { kind: "monster" }));
  return { source, ally, battle: { heroes: [source, ally], monsters: [enemy] } };
}

{
  const { source, ally, battle } = setup(template("Aurelia", { aura_of_protection_2014_bonus: 2 }));
  A.sync(battle);
  assert.equal(M.savingThrowFlat(ally.state), 2);
  assert.equal(M.savingThrowFlat(source.state), 0);
  window.IRON_PIT_DICE = { roll: () => 8, rollMany: () => [8] };
  const save = window.IRON_PIT_BROWSER_SAVES.resolveSavingThrow(ally.state, "wisdom", 12);
  assert.equal(save.roll.modifier, 4);
  assert.equal(save.succeeded, true);

  ally.position_ft = 15;
  A.sync(battle);
  assert.equal(M.savingThrowFlat(ally.state), 0);
}

{
  const { ally, battle } = setup(template("Aurelia", {
    aura_of_protection_2014_bonus: 3,
    aura_of_devotion_2014: true,
    aura_of_courage_2014: true,
  }));
  A.sync(battle);
  assert.equal(I.immune(ally.state, "charmed"), true);
  assert.equal(I.immune(ally.state, "frightened"), true);
  ally.position_ft = 15;
  A.sync(battle);
  assert.equal(I.immune(ally.state, "charmed"), false);
  assert.equal(I.immune(ally.state, "frightened"), false);
}

{
  const { source, ally, battle } = setup(template("Aurelia", { aura_of_protection_2014_bonus: 3 }));
  source.state.is_unconscious = true;
  A.sync(battle);
  assert.equal(M.savingThrowFlat(ally.state), 0);
  source.state.is_unconscious = false;
  source.state.is_alive = false;
  source.state.is_dead = true;
  source.state.current_hp = 0;
  A.sync(battle);
  assert.equal(M.savingThrowFlat(ally.state), 0);
}

{
  const { source, ally, battle } = setup(template("Aurelia", { aura_of_protection_2014_bonus: 2 }));
  const stronger = member("aurelia-8", "heroes", 5, template("Aurelia 8", { aura_of_protection_2014_bonus: 3 }));
  battle.heroes.splice(1, 0, stronger);
  A.sync(battle);
  assert.equal(M.savingThrowFlat(ally.state), 3);
  assert.equal(M.savingThrowFlat(source.state), 1);
  assert.equal(M.savingThrowFlat(stronger.state), 0);
}

console.log("2014 Paladin browser aura parity passed.");
