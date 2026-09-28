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
load("browser-saving-throws.js");

const heroes = window.IRON_PIT_BROWSER_HEROES;
const modern = heroes["rokhan-stonefury-l18"];
const legacy = heroes["rokhan-stonefury-2014-l18"];

assert.ok(modern, "generated 2024 Barbarian level 18 must exist");
assert.ok(legacy, "generated 2014 Barbarian level 18 must exist");
assert.deepEqual(modern.ability_check_minimums, [
  { source_id: "indomitable-might", ability: "strength", minimum_source: "ability_score" },
]);
assert.deepEqual(modern.saving_throw_minimums, [
  { source_id: "indomitable-might", ability: "strength", minimum_source: "ability_score" },
]);
assert.deepEqual(legacy.saving_throw_minimums || [], []);

const state = {
  template: modern,
  resources: {},
  active_effect_ids: [],
  active_modifiers: [],
};
const raw = {
  rolls: [1],
  selected_roll: 1,
  modifier: 11,
  total: 12,
  mode: "normal",
  notation: "1d20+11",
  revisions: [],
};
const revised = window.IRON_PIT_BROWSER_SAVING_THROWS.applyMinimum(state, "strength", raw);
assert.equal(revised.total, 20);
assert.equal(revised.revisions.at(-1).source_effect_id, "indomitable-might");
assert.equal(revised.revisions.at(-1).kind, "total_replacement");
assert.deepEqual(
  [revised.revisions.at(-1).original_total, revised.revisions.at(-1).replacement_total],
  [12, 20],
);

const dex = window.IRON_PIT_BROWSER_SAVING_THROWS.applyMinimum(
  state,
  "dexterity",
  { ...raw, modifier: 1, total: 2, notation: "1d20+1", revisions: [] },
);
assert.equal(dex.total, 2);
assert.deepEqual(dex.revisions, []);

console.log("Browser 2024 Indomitable Might uses universal check/save total floors without 2014 leakage.");
