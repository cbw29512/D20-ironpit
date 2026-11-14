"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

// Test schema: a seeded source preset declares observable event aspects;
// the seeded rerun must produce an identical battle fingerprint.
try {
  const context = {console};
  context.window = context;
  const filename = path.join(__dirname, "bulk-combat-validation.js");
  vm.runInNewContext(fs.readFileSync(filename, "utf8"), context, {filename});
  const inspect = context.IRON_PIT_BULK_COMBAT_VALIDATION.inspect;
  const entry = {
    kind: "preset", seed: 12345, label: "Source-backed prepared fight",
    selection: {ruleset: "2014", hero_ids: ["hero"], monster_ids: ["foe"]},
    required_aspects: [{kind: "feature", value: "tested-feature"}],
  };
  const battle = {outcome: "heroes_win", rounds: 1,
    events: [{round_number: 1, event_type: "attack",
      feature_id: "tested-feature"}]};
  let rerun = battle;
  let changedCard = false;
  const card = {id: "immutable-source"};
  const before = JSON.stringify(card);
  context.IRON_PIT_COMBAT_PRESETS = {
    aspectFired: (value, spec) => value.events.some(e => e.feature_id === spec.value),
  };
  context.IRON_PIT_BATTLE_LAB = {
    fingerprint: value => JSON.stringify(value),
  };
  context.IRON_PIT_BROWSER_TURBO = {
    runSeeded: (selection, seed) => {
      assert.equal(seed, entry.seed);
      assert.equal(selection.ruleset, "2014");
      if (changedCard) card.id = "incorrectly-mutated";
      return {battle: rerun};
    },
  };
  const problems = () => Array.from(inspect(battle, [[card, before]],
    null, entry, 12345));

  assert.deepEqual(problems(), [], "Observed preset with identical seed must pass");

  const missing = {...entry, required_aspects: [{kind: "feature", value: "missing"}]};
  assert.match(Array.from(inspect(battle, [], null, missing, 12345)).join("|"),
    /preset_required_mechanic_not_observed/,
    "The source-required feature must fire; completion alone is insufficient");

  rerun = {...battle, rounds: 2};
  assert.ok(problems().includes("seed_replay_mismatch"),
    "An identical seed must reproduce the same full combat fingerprint");
  rerun = battle;

  changedCard = true;
  assert.ok(problems().includes("source_card_mutation"),
    "Seed replay must not hide mutations to immutable source data");
  card.id = "immutable-source"; changedCard = false;

  const duet = {...entry, kind: "duel", required_aspects: undefined};
  context.IRON_PIT_COMBAT_PRESETS = null;
  assert.deepEqual(Array.from(inspect(battle, [], null, duet, 12345)), [],
    "Ordinary duels must not require the preset-only verifier");
  assert.throws(() => inspect(battle, [], null, entry, 12345),
    /Preset certification dependencies are unavailable/);

  // The production runner must pass source plan and seed into its validator.
  const runner = fs.readFileSync(path.join(__dirname,
    "bulk-combat-runner.js"), "utf8");
  assert.match(runner, /battle,\s*originals,\s*bagActorId,\s*entry,\s*seed/);
  console.log("Hero bulk preset feature evidence, seed parity, and source immutability passed.");
} catch (error) {
  console.error("Hero bulk preset certification regression failed", error);
  process.exitCode = 1;
}
