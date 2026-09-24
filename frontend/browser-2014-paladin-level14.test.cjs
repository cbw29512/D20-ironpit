"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

load("browser-action-economy.js");
load("browser-modifiers.js");
load("browser-state.js");
load("browser-spellcasting.js");
load("browser-effect-removal.js");

const S = window.IRON_PIT_BROWSER_STATE;
const M = window.IRON_PIT_BROWSER_MODIFIERS;
const ER = window.IRON_PIT_BROWSER_EFFECT_REMOVAL;

function template(name, extra = {}) {
  return {
    id: name.toLowerCase().replaceAll(" ", "-"),
    name,
    level: 14,
    kind: "character",
    ruleset: "2014",
    size: "medium",
    armor_class: 15,
    max_hp: 30,
    speed_ft: 30,
    initiative_bonus: 0,
    condition_immunities: [],
    traits: [],
    resources: {},
    ability_scores: {
      strength: 16, dexterity: 10, constitution: 14,
      intelligence: 8, wisdom: 12, charisma: 17,
    },
    saving_throw_bonuses: {
      strength: 3, dexterity: 0, constitution: 2,
      intelligence: -1, wisdom: 1, charisma: 6,
    },
    attacks: [],
    defensive_spell_actions: [],
    effect_removal_actions: [],
    ...extra,
  };
}

function member(id, side, position, tpl) {
  return { combatant_id: id, side, position_ft: position, state: S.buildState(tpl) };
}

const cleansing = {
  id: "cleansing-touch",
  name: "Cleansing Touch",
  level: 0,
  actionCost: "action",
  range: 5,
  castingAbility: null,
  targetMode: "self_or_ally",
  autoRemoveMaxLevel: 9,
  resourceId: "cleansing-touch",
  resourceCost: 1,
  expendsSpellSlot: false,
  animation: "cleansing-touch",
};
const deathWard = {
  id: "death-ward", name: "Death Ward", level: 4,
  actionCost: "action", range: 5, durationMinutes: 480,
  targetPolicy: "friendly", targetCount: 1, concentration: false,
  modifierEffects: [],
};
const hostileSpell = {
  id: "hostile-test-spell", name: "Hostile Test Spell", level: 4,
  actionCost: "action", range: 30, durationMinutes: 1,
  targetPolicy: "friendly", targetCount: 1, concentration: false,
  modifierEffects: [],
};

const paladin = member("aurelia", "heroes", 0, template("Aurelia", {
  resources: { "cleansing-touch": 3, "spell-slot-4": 1 },
  defensive_spell_actions: [deathWard],
  effect_removal_actions: [cleansing],
}));
const ally = member("ally", "heroes", 5, template("Ally"));
const enemy = member("enemy", "monsters", 10, template("Enemy", {
  kind: "monster",
  defensive_spell_actions: [hostileSpell],
}));

M.add(ally.state, {
  id: "aurelia:death-ward:ally:0",
  source_id: paladin.combatant_id,
  source_effect_id: "death-ward",
  source_name: "Death Ward",
  source_is_magical: true,
  kind: "zero-hp-replacement",
  replacement_hp: 1,
  prevents_instant_death: true,
  target_id: ally.combatant_id,
});
M.add(ally.state, {
  id: "enemy:hostile-test-spell:ally:0",
  source_id: enemy.combatant_id,
  source_effect_id: "hostile-test-spell",
  source_name: "Hostile Test Spell",
  source_is_magical: true,
  kind: "armor-class",
  flat_bonus: -1,
  target_id: ally.combatant_id,
});

const setup = { heroes: [paladin, ally], monsters: [enemy] };
const choice = ER.choose(paladin, setup, "1:aurelia");
assert.ok(choice);
assert.equal(choice.action.id, "cleansing-touch");
assert.equal(choice.effect.target.combatant_id, "ally");
assert.equal(choice.effect.source.combatant_id, "enemy");
assert.equal(choice.effect.effectId, "hostile-test-spell");

const beforeSlot = paladin.state.resources["spell-slot-4"];
const event = ER.resolve(
  1, 1, paladin, setup, choice.action, choice.effect, "1:aurelia",
);

assert.equal(paladin.state.action_available, false);
assert.equal(paladin.state.resources["cleansing-touch"], 2);
assert.equal(paladin.state.resources["spell-slot-4"], beforeSlot);
assert.equal(event.ability_check_roll, null);
assert.equal(event.check_dc, null);
assert.deepEqual(event.removed_condition_ids, ["hostile-test-spell"]);
assert.ok(!ally.state.active_modifiers.some((item) => item.source_effect_id === "hostile-test-spell"));
assert.ok(ally.state.active_modifiers.some((item) => item.source_effect_id === "death-ward"));

console.log("2014 Paladin level 14 Cleansing Touch browser parity passed.");
