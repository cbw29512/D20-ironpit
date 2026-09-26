"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

load("browser-opening-modifiers.js");
load("browser-debuff-counters.js");
load("browser-condition-immunity.js");
load("browser-condition-rules.js");
load("browser-modifiers.js");
load("browser-grapple.js");
load("browser-timed-conditions.js");
load("browser-state.js");

const C = window.IRON_PIT_BROWSER_DEBUFF_COUNTERS;
const G = window.IRON_PIT_BROWSER_GRAPPLE;
const M = window.IRON_PIT_BROWSER_MODIFIERS;
const S = window.IRON_PIT_BROWSER_STATE;
const T = window.IRON_PIT_BROWSER_TIMED;

function state(name = "Target") {
  return S.buildState({
    id: name.toLowerCase(), name, max_hp: 20, speed_ft: 30,
    condition_immunities: [], resources: {}, traits: [],
  });
}

function addCounter(target, id, counter) {
  M.add(target, {
    id: `counter:${id}`,
    source_id: "buff-source",
    source_effect_id: "test-buff",
    kind: "debuff-counter",
    debuff_counter: counter,
  });
}

{
  const target = state("Magical Condition");
  addCounter(target, 1, { debuff_id: "paralyzed", source_scope: "magical", mode: "prevent", movement_cost_ft: 0 });
  assert.equal(T.apply(target, "paralyzed", "spell", {
    sourceIsMagical: true, useDefaultPoisonRecovery: false,
  }), null);
  assert.equal(T.apply(target, "paralyzed", "monster", {
    sourceIsMagical: false, useDefaultPoisonRecovery: false,
  }), "paralyzed");
}

{
  const magical = state("Magical Slow");
  addCounter(magical, 1, { debuff_id: "speed-reduction", source_scope: "magical", mode: "prevent", movement_cost_ft: 0 });
  M.add(magical, {
    id: "slow:magical", source_id: "spell", source_effect_id: "slow",
    source_is_magical: true, kind: "speed", flat_bonus: -10,
  });
  assert.equal(M.effectiveSpeed(magical), 30);

  const nonmagical = state("Nonmagical Slow");
  addCounter(nonmagical, 1, { debuff_id: "speed-reduction", source_scope: "magical", mode: "prevent", movement_cost_ft: 0 });
  M.add(nonmagical, {
    id: "slow:nonmagical", source_id: "terrain", source_effect_id: "hampered",
    source_is_magical: false, kind: "speed", flat_bonus: -10,
  });
  assert.equal(M.effectiveSpeed(nonmagical), 20);
}

{
  const target = state("Grappled");
  addCounter(target, 1, {
    debuff_id: "grappled", source_scope: "nonmagical",
    mode: "remove-with-movement", movement_cost_ft: 5,
  });
  addCounter(target, 2, {
    debuff_id: "restrained", source_scope: "nonmagical",
    mode: "remove-with-movement", movement_cost_ft: 5,
  });
  assert.deepEqual(G.apply(target, "crocodile", 12, 5, true, false), ["grappled", "restrained"]);
  const resolved = S.beginTurn(target);
  assert.deepEqual(resolved, [{ debuffId: "restrained", sourceId: "crocodile", movementCost: 5 }]);
  assert.equal(target.grapple_sources.length, 0);
  assert.equal(target.movement_remaining_ft, 25);
}

{
  const target = state("Magical Grapple Speed");
  addCounter(target, 1, {
    debuff_id: "speed-reduction", source_scope: "magical",
    mode: "prevent", movement_cost_ft: 0,
  });
  G.apply(target, "magic-source", 12, 5, false, true);
  assert.deepEqual(S.beginTurn(target), []);
  assert.equal(target.grapple_sources.length, 1);
  assert.equal(target.movement_remaining_ft, 30);
}

{
  const target = state("Magic Grapple");
  addCounter(target, 1, {
    debuff_id: "grappled", source_scope: "nonmagical",
    mode: "remove-with-movement", movement_cost_ft: 5,
  });
  G.apply(target, "magic-source", 12, 5, false, true);
  assert.deepEqual(S.beginTurn(target), []);
  assert.equal(target.grapple_sources.length, 1);
  assert.equal(target.movement_remaining_ft, 0);
}

{
  const target = state("Terrain");
  assert.equal(C.difficultTerrainMultiplier(target), 2);
  addCounter(target, 1, {
    debuff_id: "difficult-terrain", source_scope: "any",
    mode: "prevent", movement_cost_ft: 0,
  });
  assert.equal(C.difficultTerrainMultiplier(target), 1);
}

{
  const template = {
    id: "land-druid",
    name: "Land Druid",
    max_hp: 20,
    speed_ft: 30,
    condition_immunities: [],
    resources: {},
    traits: [],
    passive_debuff_counter_grants: [{
      source_id: "lands-stride",
      source_name: "Land's Stride",
      counter: {
        debuff_id: "difficult-terrain",
        source_scope: "nonmagical",
        mode: "prevent",
        movement_cost_ft: 0,
      },
    }],
  };
  const target = S.buildState(template);
  assert.equal(C.difficultTerrainMultiplier(target, { sourceIsMagical: false }), 1);
  assert.equal(C.difficultTerrainMultiplier(target, { sourceIsMagical: true }), 2);
  const grant = target.active_modifiers.find((item) => item.source_effect_id === "lands-stride");
  assert.ok(grant);
  assert.equal(grant.source_name, "Land's Stride");
  assert.equal(grant.kind, "debuff-counter");
}

console.log("Universal browser buff/debuff counters passed.");
