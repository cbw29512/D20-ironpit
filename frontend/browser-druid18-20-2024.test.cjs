"use strict";

const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

const heroes = window.IRON_PIT_BROWSER_HEROES;
const monsters = window.IRON_PIT_BROWSER_MONSTERS;
const l18 = heroes["thalen-greenbough-l18"];
const l19 = heroes["thalen-greenbough-l19"];
const l20 = heroes["thalen-greenbough-l20"];

assert.ok(l18 && l19 && l20, "2024 Druid 18-20 must exist in generated browser heroes.");
assert.deepEqual([l18.max_hp, l19.max_hp, l20.max_hp], [93, 98, 103]);

const shape = l18.replacement_form_actions[0];
assert.equal(shape.retainSpellcasting, true);
assert.ok(shape.retainedSpellActionIds.includes("wall-of-stone"));
assert.ok(!shape.retainedSpellActionIds.includes("lands-aid"));
const form = monsters[shape.formTemplateId];
const active = window.IRON_PIT_BROWSER_REPLACEMENT_FORM_COMPILER.compile(
  l18, form, true, shape.retainedSpellActionIds, true, true,
);
assert.deepEqual(active.persistent_barrier_actions.map((item) => item.id), ["wall-of-stone"]);
assert.ok(active.defensive_spell_actions.some((item) => item.id === "barkskin"));

assert.equal(l19.ability_scores.intelligence, 14);
assert.equal(l19.resources["boon-of-fate"], 1);
assert.equal(l19.resource_backed_d20_outcome_adjustments[0].source_id, "boon-of-fate");
assert.ok(l19.initiative_resource_refill_grants.some((item) => item.source_id === "boon-of-fate"));
assert.equal(l19.canonical_prepared_spells.at(-1).id, "regenerate");

const state = window.IRON_PIT_BROWSER_STATE.buildState(structuredClone(l20));
state.resources["spell-slot-8"] = 0;
const conversion = window.IRON_PIT_BROWSER_RESOURCE_CONVERSION.automaticAction(state);
assert.equal(conversion.id, "nature-magician-level-8");
const member = { combatant_id: "thalen", side: "heroes", position_ft: 0, state };
const conversionEvent = window.IRON_PIT_BROWSER_RESOURCE_CONVERSION.resolve(
  1, 1, member, conversion, "1:thalen",
);
assert.equal(conversionEvent.feature_id, "nature-magician-level-8");
assert.equal(state.resources["spell-slot-8"], 1);
assert.equal(state.resources["wild-shape"], 0);
assert.equal(state.resources["nature-magician-conversion"], 0);

state.resources["wild-shape"] = 0;
const refill = window.IRON_PIT_BROWSER_INITIATIVE_RESOURCE_REFILL.resolve(
  2, { heroes: [member], monsters: [] },
);
assert.ok(refill.events.some((item) => item.feature_id === "evergreen-wild-shape"));
assert.equal(state.resources["wild-shape"], 1);
assert.equal(l20.canonical_prepared_spells.at(-1).id, "ice-storm");
const ice = l20.spell_save_actions.find((item) => item.id === "ice-storm");
assert.ok(ice, "Ice Storm must bind its printed Difficult Terrain rider.");
assert.equal(ice.createsDifficultTerrain, true);
assert.equal(ice.difficultTerrainDurationRounds, 1);

console.log("Generated browser 2024 Druid levels 18-20 endgame parity passed.");
