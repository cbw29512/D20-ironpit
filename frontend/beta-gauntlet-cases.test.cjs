"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const test = require("node:test");

function load() {
  try {
    const source = fs.readFileSync(path.join(__dirname, "beta-gauntlet-cases.js"), "utf8");
    const context = { window: {} };
    vm.runInNewContext(source, context, { filename: "beta-gauntlet-cases.js" });
    return context.window.IRON_PIT_BETA_GAUNTLET_CASES;
  } catch (error) {
    console.error("Unable to initialize beta matchup test", error);
    throw error;
  }
}

test("synthetic cards resolve to source-neutral combatant IDs", () => {
  const cases = load();
  const recipe = { ruleset: "2014" };
  const catalog = {};
  const presets = { resolve: () => ({
    heroes: [{ runnable_template_id: "synthetic-hero" }],
    monsters: [{ runnable_template_id: "synthetic-monster" }],
  }) };
  const selected = cases.selection(recipe, catalog, presets);
  assert.equal(selected.ruleset, "2014");
  assert.deepEqual(Array.from(selected.hero_ids), ["synthetic-hero"]);
  assert.deepEqual(Array.from(selected.monster_ids), ["synthetic-monster"]);
});

test("roster sweep covers every runnable card at least once", async () => {
  const cases = load();
  const cards = {
    heroes: ["a", "b", "c"].map((id) => ({ name: id, coverage_status: "raw_ready", runnable_template_id: id })),
    monsters: ["x", "y"].map((id) => ({ name: id, coverage_status: "raw_ready", runnable_template_id: id })),
  };
  const runtime = { IRON_PIT_BROWSER_CATALOG: { buildCatalog: async () => cards } };
  const sweep = await cases.rosterSweep(runtime, ["2014"]);
  assert.equal(sweep.length, 3);
  assert.deepEqual(Array.from(sweep, (row) => row.selection.hero_ids[0]), ["a", "b", "c"]);
  assert.deepEqual(Array.from(new Set(sweep.map((row) => row.selection.monster_ids[0]))), ["x", "y"]);
});

test("missing expected ability fails a fight without accepting empty evidence", () => {
  const cases = load();
  const replay = { battle: { events: [{ event_type: "victory" }], outcome: "heroes_win", rounds: 1 } };
  const recipe = { aspects: [{ kind: "feature", value: "synthetic" }] };
  const presets = { aspectFired: () => false };
  assert.throws(() => cases.validate(replay, recipe, presets, true), /Missing expected/);
  assert.match(cases.validate(replay, recipe, presets, false), /1 events/);
  assert.throws(() => cases.validate({ battle: { ...replay.battle, events: [] } }, recipe, presets, false), /No battle events/);
});
