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

load("browser-heroes.js");
load("browser-opening-modifiers.js");
load("browser-debuff-counters.js");
load("browser-defensive-modifier-rules.js");
load("browser-condition-immunity.js");

const hero = window.IRON_PIT_BROWSER_HEROES["thalen-greenbough-2014-l10"];
assert.ok(hero);
assert.deepEqual(hero.damage_immunities, ["poison"]);
assert.equal(hero.canonical_prepared_spells.length, 15);
assert.equal(hero.canonical_prepared_spells.at(-1).id, "scrying");

const state = {
  template: hero,
  active_modifiers: window.IRON_PIT_BROWSER_OPENING_MODIFIERS.build(hero),
  timed_effects: [],
  active_effect_ids: [],
  active_buff_effect_ids: [],
};

const counters = window.IRON_PIT_BROWSER_DEBUFF_COUNTERS;
const immunity = window.IRON_PIT_BROWSER_CONDITION_IMMUNITY;

assert.equal(counters.prevented(state, "poisoned"), true);
assert.equal(counters.prevented(state, "disease"), true);

assert.equal(immunity.immune(state, "charmed", { creature_type: "fey" }), true);
assert.equal(immunity.immune(state, "frightened", { creature_type: "elemental" }), true);
assert.equal(immunity.immune(state, "charmed", { creature_type: "humanoid" }), false);
assert.equal(immunity.immune(state, "frightened", { creature_type: "humanoid" }), false);

const ward = state.active_modifiers.filter((item) => item.source_effect_id === "natures-ward");
assert.equal(ward.length, 4);
assert.ok(ward.every((item) => item.source_name === "Nature's Ward"));

console.log("2014 Druid level 10 Nature's Ward check/result parity passed.");
