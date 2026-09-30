"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

load("browser-heroes.js");

const hero = window.IRON_PIT_BROWSER_HEROES["thalen-greenbough-l8"];
assert.ok(hero, "2024 Druid 8 must exist in generated browser heroes.");
assert.equal(hero.level, 8);
assert.equal(hero.max_hp, 43);
assert.equal(hero.ability_scores.wisdom, 20);
assert.equal(hero.ability_scores.charisma, 16);
assert.equal(hero.saving_throw_bonuses.wisdom, 8);
assert.deepEqual(hero.resources, {
  "spell-slot-1": 4,
  "spell-slot-2": 3,
  "spell-slot-3": 3,
  "spell-slot-4": 2,
  "wild-shape": 3,
  "wild-resurgence-slot-restore": 1,
  "natural-recovery-free-cast": 1,
});

assert.equal(hero.canonical_prepared_spells.length, 12);
assert.equal(hero.canonical_prepared_spells.at(-1).id, "freedom-of-movement");

const form = hero.replacement_form_actions[0];
assert.equal(form.id, "wild-shape");
assert.equal(form.formTemplateId, "srd-brown-bear");
assert.equal(form.actionCost, "bonus_action");
assert.equal(form.hpMode, "retain_owner");
assert.equal(form.temporaryHpOnEnter, 8);
assert.equal(form.retainCreatureType, true);
assert.equal(form.replaceExistingForm, true);

const spell = hero.defensive_spell_actions.find((item) => item.id === "freedom-of-movement");
assert.ok(spell, "Druid 8 must expose 2024 Freedom of Movement.");
assert.equal(spell.level, 4);
assert.equal(spell.actionCost, "action");
assert.equal(spell.range, 5);
assert.equal(spell.durationMinutes, 60);
assert.equal(spell.targetPolicy, "friendly");
assert.equal(spell.targetCount, 1);
assert.equal(spell.targetCountPerSlotAbove, 1);
assert.equal(spell.concentration, false);
assert.deepEqual(spell.movementModeGrants, [
  { mode: "swim", fixedSpeedFt: null, matchCurrentSpeed: true },
]);

const signatures = spell.modifierEffects
  .filter((item) => item.debuffCounter)
  .map((item) => [
    item.debuffCounter.debuff_id,
    item.debuffCounter.source_scope,
    item.debuffCounter.mode,
    item.debuffCounter.movement_cost_ft,
  ])
  .sort();
assert.deepEqual(signatures, [
  ["difficult-terrain", "any", "prevent", 0],
  ["grappled", "nonmagical", "remove-with-movement", 5],
  ["paralyzed", "magical", "prevent", 0],
  ["restrained", "magical", "prevent", 0],
  ["restrained", "nonmagical", "remove-with-movement", 5],
  ["speed-reduction", "magical", "prevent", 0],
].sort());

console.log("Generated browser 2024 Druid 8 progression regressions passed.");
