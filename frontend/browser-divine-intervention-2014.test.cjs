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
  "browser-heroes.js",
  "browser-condition-immunity.js",
  "browser-condition-rules.js",
  "browser-state.js",
  "browser-action-economy.js",
  "browser-healing-policy.js",
  "browser-healing-resolution.js", "browser-healing.js",
  "browser-group-healing.js",
]) load(file);

window.IRON_PIT_BROWSER_SPELLCASTING = {
  slotSpellAvailable: () => true,
  markSlotSpellCast: () => {},
};
window.IRON_PIT_BROWSER_SPELL_AREA = {
  bestFriendlyPlacement: () => null,
};

const S = window.IRON_PIT_BROWSER_STATE;
const H = window.IRON_PIT_BROWSER_HEALING;

const template = (level = 10) => structuredClone(
  Object.values(window.IRON_PIT_BROWSER_HEROES)
    .find((hero) => hero.ruleset === "2014" && hero.class_id === "cleric" && hero.level === level),
);

const member = (id, hp, level = 10) => {
  const state = S.buildState(template(level));
  state.current_hp = hp;
  return { combatant_id: id, side: "heroes", position_ft: 0, state };
};

const setup = (cleric, ally) => ({ heroes: [cleric, ally], monsters: [] });

{
  const cleric = member("cleric", 60);
  const ally = member("ally", 10);
  const action = cleric.state.template.healingActions
    .find((item) => item.id === "divine-intervention");

  assert.ok(action);
  assert.equal(action.restoreToEffectiveMax, true);
  assert.equal(action.percentileSuccessMax, 10);
  assert.equal(action.resourceId, "divine-intervention");

  const choice = H.chooseAction(cleric, setup(cleric, ally), "1:cleric");
  assert.equal(choice.action.id, "divine-intervention");
  assert.equal(choice.target.combatant_id, "ally");
}

{
  const cleric = member("cleric", 60);
  const ally = member("ally", 10);
  const action = cleric.state.template.healingActions
    .find((item) => item.id === "divine-intervention");

  window.IRON_PIT_DICE = { roll: () => 11 };
  const before = ally.state.current_hp;
  const event = H.resolve(1, 1, cleric, ally, action, "1:cleric");

  assert.equal(event.event_type, "feature");
  assert.equal(event.feature_roll.total, 11);
  assert.equal(ally.state.current_hp, before);
  assert.equal(event.resource_remaining, 0);
  assert.equal(cleric.state.resources["divine-intervention"], 0);
}

{
  const cleric = member("cleric", 60);
  const ally = member("ally", 10);
  const action = cleric.state.template.healingActions
    .find((item) => item.id === "divine-intervention");

  window.IRON_PIT_DICE = { roll: () => 10 };
  const event = H.resolve(1, 1, cleric, ally, action, "1:cleric");

  assert.equal(event.event_type, "healing");
  assert.equal(event.feature_roll.total, 10);
  assert.equal(event.healing_roll.notation, "restore-to-effective-max");
  assert.equal(ally.state.current_hp, S.effectiveMaxHp(ally.state));
  assert.equal(event.resource_remaining, 0);
}

{
  const cleric = member("cleric-20", 100, 20);
  const ally = member("ally-19", 10, 19);
  const action = cleric.state.template.healingActions
    .find((item) => item.id === "divine-intervention");

  assert.ok(action);
  assert.equal(action.restoreToEffectiveMax, true);
  assert.equal(action.percentileSuccessMax, null);
  assert.equal(action.resourceId, "divine-intervention");

  window.IRON_PIT_DICE = {
    roll: (sides) => {
      throw new Error(`Level-20 Divine Intervention must not roll d${sides}.`);
    },
  };
  const event = H.resolve(1, 1, cleric, ally, action, "1:cleric-20");

  assert.equal(event.event_type, "healing");
  assert.equal(event.feature_roll, null);
  assert.equal(event.healing_roll.notation, "restore-to-effective-max");
  assert.equal(ally.state.current_hp, S.effectiveMaxHp(ally.state));
  assert.equal(event.resource_remaining, 0);
  assert.equal(cleric.state.resources["divine-intervention"], 0);
}

console.log("Browser 2014 Divine Intervention percentile and level-20 automatic-success regressions passed.");
