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
  "browser-opening-modifiers.js",
  "browser-debuff-counters.js",
  "browser-flight-ground-immunity.js",
  "browser-condition-immunity.js",
  "browser-condition-rules.js",
  "browser-modifier-validation.js",
  "browser-modifiers.js",
  "browser-grapple.js",
  "browser-timed-conditions.js",
  "browser-state.js",
  "browser-action-economy.js",
  "browser-grid-geometry.js",
  "browser-pit-engagement.js",
  "browser-grid-barriers.js",
  "browser-grid-movement-support.js",
  "browser-grid-path-search-support.js",
  "browser-grid-path-search.js",
  "browser-grid-movement.js",
  "browser-teleport-cancel.js",
  "browser-teleport.js",
  "browser-monsters-2014.js",
]) load(file);

const C = window.IRON_PIT_BROWSER_DEBUFF_COUNTERS;
const F = window.IRON_PIT_BROWSER_FLIGHT_GROUND;
const G = window.IRON_PIT_BROWSER_GRAPPLE;
const M = window.IRON_PIT_BROWSER_GRID_MOVEMENT;
const P = window.IRON_PIT_BROWSER_PIT_ENGAGEMENT;
const S = window.IRON_PIT_BROWSER_STATE;
const T = window.IRON_PIT_BROWSER_TIMED;
const TP = window.IRON_PIT_BROWSER_TELEPORT;
const map = { id: "pit-lock", width_squares: 16, height_squares: 16, cell_size_ft: 5 };

function member(id, side, x, y, extras = {}) {
  const state = S.buildState({
    id, name: id, max_hp: 20, speed_ft: 30, size: "medium",
    movement_modes: { walk_ft: 30, fly_ft: extras.flyFt || 0, climb_ft: 0, swim_ft: 0, burrow_ft: 0, hover: false },
    condition_immunities: [], resources: extras.resources || {}, traits: [],
    teleport_actions: extras.teleportActions || [],
  });
  state.position = { x, y };
  state.action_available = true;
  state.bonus_action_available = true;
  return { combatant_id: id, side, state };
}

{
  const flyer = member("flyer", "heroes", 7, 6, { flyFt: 60 });
  const enemy = member("enemy", "monsters", 8, 6);
  assert.equal(F.isFlying(flyer.state), true);
  assert.equal(T.apply(flyer.state, "restrained", "enemy", {
    sourceEffectId: "ground-snare",
    sourceIsMagical: true,
    groundContact: true,
    useDefaultPoisonRecovery: false,
  }), null);
  assert.equal(flyer.state.active_effect_ids.includes("restrained"), false);
  assert.equal(C.difficultTerrainMultiplier(flyer.state, { sourceIsMagical: true }), 1);

  const walker = member("walker", "heroes", 7, 7);
  assert.equal(T.apply(walker.state, "restrained", "enemy", {
    sourceEffectId: "ground-snare",
    sourceIsMagical: true,
    groundContact: true,
    useDefaultPoisonRecovery: false,
  }), "restrained");
  assert.equal(C.difficultTerrainMultiplier(walker.state, { sourceIsMagical: true }), 2);

  assert.equal(P.leavesMelee(flyer, [flyer, enemy], { x: 5, y: 6 }), true);
  assert.equal(M.movementStepCostFt(map, flyer, { x: 5, y: 6 }, [flyer, enemy]), 5);
  const plan = M.planToward(map, flyer, enemy, [flyer, enemy], 25, 60);
  assert.deepEqual(plan.path, []);
  assert.deepEqual(flyer.state.position, { x: 7, y: 6 });
}

{
  const flyer = member("seeded-flyer", "heroes", 4, 4, { flyFt: 40 });
  T.apply(flyer.state, "poisoned", "seed", { useDefaultPoisonRecovery: false });
  flyer.state.timed_effects.push({
    effect_id: "restrained",
    source_id: "seed",
    source_effect_id: "ground-snare",
    ground_contact: true,
    ends_on_teleport: true,
  });
  flyer.state.active_effect_ids.push("restrained");
  const cleared = S.beginTurn(flyer.state);
  assert.ok(cleared.some((item) => item.debuffId === "restrained" && item.movementCost === 0));
  assert.equal(flyer.state.active_effect_ids.includes("restrained"), false);
  assert.equal(flyer.state.active_effect_ids.includes("poisoned"), true);
}

{
  const caster = member("caster", "heroes", 6, 6, {
    resources: { "spell-slot-2": 1 },
    teleportActions: [{
      id: "misty-step",
      name: "Misty Step",
      level: 2,
      actionCost: "bonus_action",
      range: 30,
      resourceId: "spell-slot-2",
      resourceCost: 1,
      expendsSpellSlot: true,
      animation: "misty-step",
    }],
  });
  const enemy = member("enemy", "monsters", 7, 6);
  const origin = { ...caster.state.position };
  assert.equal(T.apply(caster.state, "restrained", "enemy", {
    sourceEffectId: "ground-snare",
    sourceIsMagical: true,
    groundContact: true,
    endsOnTeleport: true,
    useDefaultPoisonRecovery: false,
  }), "restrained");
  G.apply(caster.state, "enemy", 12, 5, true);
  S.beginTurn(caster.state);
  const choice = TP.choose(caster, { heroes: [caster], monsters: [enemy], map_definition: map }, "1:caster");
  assert.equal(choice.action.id, "misty-step");
  assert.deepEqual(choice.destination, origin);
  const resolved = TP.resolve(1, 1, caster, { heroes: [caster], monsters: [enemy] }, choice.action, choice.destination, "1:caster");
  assert.deepEqual(caster.state.position, origin);
  assert.equal(caster.state.active_effect_ids.includes("restrained"), false);
  assert.deepEqual(caster.state.grapple_sources, []);
  assert.equal(resolved.events[0].event_type, "feature");
  assert.ok(resolved.events[0].removed_condition_ids.includes("restrained"));
  assert.match(resolved.events[0].description, /without leaving its spot/);
}

{
  const caster = member("door-caster", "heroes", 1, 2, {
    resources: { "spell-slot-4": 1 },
    teleportActions: [{
      id: "dimension-door",
      name: "Dimension Door",
      level: 4,
      actionCost: "action",
      range: 500,
      resourceId: "spell-slot-4",
      resourceCost: 1,
      expendsSpellSlot: true,
      animation: "dimension-door",
    }],
  });
  const enemy = member("door-enemy", "monsters", 8, 2);
  const origin = { ...caster.state.position };
  assert.equal(T.apply(caster.state, "restrained", "enemy", {
    sourceEffectId: "ground-snare",
    sourceIsMagical: true,
    groundContact: true,
    endsOnTeleport: true,
    useDefaultPoisonRecovery: false,
  }), "restrained");
  const setup = { heroes: [caster], monsters: [enemy], map_definition: map };
  const resolved = TP.resolve(
    1, 1, caster, setup, caster.state.template.teleport_actions[0], { x: 7, y: 2 }, "1:door-caster",
  );
  assert.deepEqual(caster.state.position, origin);
  assert.equal(caster.state.active_effect_ids.includes("restrained"), false);
  assert.equal(resolved.events[0].feature_id, "dimension-door");
  assert.equal(resolved.events[0].event_type, "feature");
  assert.match(resolved.events[0].description, /Dimension Door/);
  assert.match(resolved.events[0].description, /without leaving its spot/);
  assert.deepEqual(TP.chooseDestination(caster, setup, caster.state.template.teleport_actions[0]), origin);
}

{
  const runner = member("runner", "heroes", 4, 4);
  const flyer = member("flyer", "monsters", 8, 4, { flyFt: 60 });
  const enemy = member("anchor", "monsters", 5, 4);
  const heroAnchor = member("hero-anchor", "heroes", 9, 4);
  assert.equal(P.leavesMelee(runner, [runner, enemy], { x: 2, y: 4 }), true);
  assert.equal(M.movementStepCostFt(map, runner, { x: 2, y: 4 }, [runner, enemy]), 5);
  assert.deepEqual(M.planToward(map, runner, enemy, [runner, enemy], 40, 60).path, []);
  assert.deepEqual(runner.state.position, { x: 4, y: 4 });
  assert.equal(M.movementStepCostFt(map, flyer, { x: 12, y: 4 }, [flyer, heroAnchor]), 5);
  assert.deepEqual(M.planToward(map, flyer, heroAnchor, [flyer, heroAnchor], 40, 60).path, []);
  assert.deepEqual(flyer.state.position, { x: 8, y: 4 });
  assert.equal(F.isFlying(flyer.state), true);
  const closer = member("closer", "monsters", 0, 4);
  const closePlan = M.planToward(map, runner, closer, [runner, enemy, closer], 5, 30);
  assert.ok(closePlan.path.length);
  assert.ok(closePlan.final_distance_ft <= 5);
  assert.equal(P.leavesMelee(runner, [runner, enemy, closer], closePlan.path[0]), true);
}

{
  const footprint = { tiny: 1, small: 1, medium: 1, large: 2, huge: 3, gargantuan: 4 };
  for (const id of ["2014-flying-snake", "2014-giant-owl", "2014-owl", "2014-pteranodon"]) {
    const template = window.IRON_PIT_BROWSER_MONSTERS_2014[id];
    const state = S.buildState(structuredClone(template));
    state.position = { x: 6, y: 6 };
    const flyer = { combatant_id: id, side: "monsters", state };
    const side = footprint[String(template.size).toLowerCase()] || 1;
    const hero = member("hero-anchor", "heroes", 6 + side, 6);
    assert.equal((template.movement_modes || {}).fly_ft, 60, `${id} must keep printed fly 60`);
    assert.equal(F.isFlying(flyer.state), true);
    assert.equal(P.leavesMelee(flyer, [flyer, hero], { x: 4, y: 6 }), true);
    assert.deepEqual(M.planToward(map, flyer, hero, [flyer, hero], 40, 60).path, []);
    assert.deepEqual(flyer.state.position, { x: 6, y: 6 });
  }
}

{
  const roc = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-roc"];
  assert.ok(roc, "2014 Roc must be in the browser roster");
  assert.equal(roc.speed_ft, 120, "2014 flyers use printed Fly as arena closing speed");
  assert.equal(roc.movement_modes.walk_ft, 20);
  assert.equal(roc.movement_modes.fly_ft, 120);
  assert.deepEqual(roc.attack_action.slots.map((slot) => slot.attackIds), [["2014-roc-beak"], ["2014-roc-talons"]]);
}
console.log("Browser pit engagement, flight, and in-place teleport regressions passed.");
