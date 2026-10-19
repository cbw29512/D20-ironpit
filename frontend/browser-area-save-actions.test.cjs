"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

window.IRON_PIT_BROWSER_GRID_GEOMETRY = {
  occupiedCells: (position) => [[position.x, position.y]],
};
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => Boolean(state[`${cost}_available`]),
  spend: (state, cost) => { state[`${cost}_available`] = false; },
};
const calls = [];
window.IRON_PIT_BROWSER_SAVES = {
  legalAction: () => true,
  resolveAction: (sequence, round, actor, target, action, distance, options) => {
    calls.push({ target: target.combatant_id, rolls: options.sharedDamageRolls ? [...options.sharedDamageRolls] : [] });
    return {
      sequence, round_number: round, event_type: "saving_throw",
      actor_id: actor.combatant_id, target_id: target.combatant_id,
      resource_remaining: options.resourceRemaining,
      damage_components: options.sharedDamageRolls ? [{ rolls: [...options.sharedDamageRolls] }] : [],
    };
  },
};
window.IRON_PIT_DICE = { rollMany: () => [1, 2] };

load("browser-area-shapes.js");
load("browser-area-targeting.js");
load("browser-area-save-actions.js");

function member(id, side, x, y) {
  return {
    combatant_id: id, side, position_ft: x * 5,
    state: {
      position: { x, y }, is_alive: true, is_dead: false, current_hp: 10,
      action_available: true, bonus_action_available: true, reaction_available: true, resources: {},
      grapple_sources: [], template: { size: "medium", max_hp: 10, saving_throw_actions: [] },
    },
  };
}

const actor = member("monster:breather", "monsters", 1, 1);
const first = member("hero:first", "heroes", 2, 1);
const second = member("hero:second", "heroes", 3, 1);
const action = {
  id: "fire-breath", name: "Fire Breath", saveAbility: "dexterity", dc: 12,
  range: 15, area: { shape: "cone", origin: "self", length_ft: 15 },
  damageDiceCount: 2, damageDiceSize: 6, damageType: "fire",
  successDamage: "half", resourceId: "fire-breath", resourceCost: 1,
};
actor.state.template.saving_throw_actions = [action];
actor.state.resources["fire-breath"] = 1;
const setup = {
  heroes: [first, second], monsters: [actor],
  map_definition: { width_squares: 10, height_squares: 10 },
};

const A = window.IRON_PIT_BROWSER_AREA_SAVES;
const selected = A.choose(actor, setup);
assert.ok(selected);
assert.equal(selected.action.id, "fire-breath");
assert.deepEqual(new Set(selected.placement.targetIds), new Set(["hero:first", "hero:second"]));

const result = A.resolve(1, 1, actor, setup, selected);
assert.equal(result.sequence, 3);
assert.equal(result.events.length, 2);
assert.equal(actor.state.resources["fire-breath"], 0);
assert.equal(actor.state.action_available, false);
assert.deepEqual(calls, [
  { target: "hero:first", rolls: [1, 2] },
  { target: "hero:second", rolls: [1, 2] },
]);
assert.ok(result.events.every((event) => event.resource_remaining === 0));

const bonusActor = member("hero:fear", "heroes", 1, 1);
const bonusTarget = member("monster:target", "monsters", 2, 1);
const bonusAction = {
  id: "fear-burst", name: "Fear Burst", actionCost: "bonus_action",
  saveAbility: "wisdom", dc: 10, range: 0,
  area: { shape: "emanation", origin: "self", radius_ft: 30 },
  damageDiceCount: 0,
};
bonusActor.state.template.saving_throw_actions = [bonusAction];
const bonusSetup = {
  heroes: [bonusActor], monsters: [bonusTarget],
  map_definition: { width_squares: 10, height_squares: 10 },
};
const bonusSelected = A.choose(bonusActor, bonusSetup);
assert.ok(bonusSelected);
const bonusResult = A.resolve(10, 1, bonusActor, bonusSetup, bonusSelected);
assert.equal(bonusResult.events.length, 1);
assert.equal(bonusActor.state.bonus_action_available, false);
assert.equal(bonusActor.state.action_available, true);

console.log("Universal browser area-save resource and action-cost parity passed.");


window.IRON_PIT_BROWSER_STATE = {
  effectiveMaxHp: (state) => state.template.max_hp,
};
window.IRON_PIT_BROWSER_HEALING = {
  restore: (state, amount) => {
    const before = state.current_hp;
    state.current_hp = Math.min(state.template.max_hp, state.current_hp + amount);
    return state.current_hp - before;
  },
};

{
  const healer = member("hero:druid", "heroes", 1, 1);
  const ally = member("hero:ally", "heroes", 2, 1);
  const enemy = member("monster:enemy", "monsters", 3, 1);
  ally.state.current_hp = 1;
  healer.state.resources["wild-shape"] = 2;
  const landsAid = {
    id: "lands-aid", name: "Land's Aid", actionCost: "action",
    saveAbility: "constitution", dc: 20, range: 60,
    area: { shape: "radius", origin: "point", radius_ft: 10 },
    damageDiceCount: 2, damageDiceSize: 6, damageType: "necrotic",
    successDamage: "half", resourceId: "wild-shape", resourceCost: 1,
    areaHealingRider: { diceCount: 2, diceSize: 6, healingBonus: 0 },
    animation: "lands-aid",
  };
  healer.state.template.saving_throw_actions = [landsAid];
  const mixedSetup = {
    heroes: [healer, ally], monsters: [enemy],
    map_definition: { width_squares: 12, height_squares: 12 },
  };
  const rolls = [[3, 4], [5, 6]];
  window.IRON_PIT_DICE = { rollMany: () => rolls.shift() };
  const mixed = A.choose(healer, mixedSetup);
  assert.ok(mixed);
  const resolved = A.resolve(20, 1, healer, mixedSetup, mixed);
  const healing = resolved.events.find((event) => event.event_type === "healing");
  assert.ok(healing);
  assert.deepEqual(healing.healing_roll.rolls, [5, 6]);
  assert.equal(healing.target_id, "hero:ally");
  assert.equal(ally.state.current_hp, 10);
  assert.equal(healer.state.resources["wild-shape"], 1);
  assert.equal(healer.state.action_available, false);
}

{
  const healer = member("hero:druid-only", "heroes", 1, 1);
  const ally = member("hero:ally-only", "heroes", 2, 1);
  ally.state.current_hp = 1;
  healer.state.resources["wild-shape"] = 2;
  healer.state.template.saving_throw_actions = [{
    id: "lands-aid", name: "Land's Aid", actionCost: "action",
    saveAbility: "constitution", dc: 13, range: 60,
    area: { shape: "radius", origin: "point", radius_ft: 10 },
    damageDiceCount: 2, damageDiceSize: 6, damageType: "necrotic",
    successDamage: "half", resourceId: "wild-shape", resourceCost: 1,
    areaHealingRider: { diceCount: 2, diceSize: 6, healingBonus: 0 },
    animation: "lands-aid",
  }];
  const healOnlySetup = {
    heroes: [healer, ally], monsters: [],
    map_definition: { width_squares: 12, height_squares: 12 },
  };
  window.IRON_PIT_DICE = { rollMany: () => [5, 6] };
  const selectedHeal = A.choose(healer, healOnlySetup);
  assert.ok(selectedHeal);
  const resolvedHeal = A.resolve(30, 1, healer, healOnlySetup, selectedHeal);
  assert.deepEqual(resolvedHeal.events.map((event) => event.event_type), ["healing"]);
  assert.equal(resolvedHeal.events[0].target_id, "hero:ally-only");
  assert.equal(healer.state.resources["wild-shape"], 1);
}


{
  // Multi-typed AOE damage is rolled once per component, then reused for
  // each affected target; defenses and saves still resolve separately.
  const jumper = member("monster:jumper", "monsters", 1, 1);
  const targets = [member("hero:one", "heroes", 2, 1), member("hero:two", "heroes", 3, 1)];
  const action = {
    id: "two-types", name: "Two Types", range: 15,
    saveAbility: "dexterity", dc: 16,
    area: { shape: "cone", origin: "self", length_ft: 15 },
    damageComponents: [
      { diceCount: 1, diceSize: 6, damageType: "bludgeoning" },
      { diceCount: 1, diceSize: 8, damageType: "slashing" },
    ],
  };
  jumper.state.template.saving_throw_actions = [action];
  const field = { heroes: targets, monsters: [jumper],
    map_definition: { width_squares: 10, height_squares: 10 } };
  const rolled = [];
  window.IRON_PIT_DICE = {
    rollMany: (count, size) => {
      rolled.push([count, size]);
      return [size];
    },
  };
  calls.length = 0;
  const selected = A.choose(jumper, field);
  assert.ok(selected);
  const resolved = A.resolve(40, 1, jumper, field, selected);
  assert.equal(resolved.events.length, 2);
  assert.deepEqual(rolled, [[1, 6], [1, 8]]);
  assert.deepEqual(calls.map((item) => item.rolls), [
    [[6], [8]], [[6], [8]],
  ]);

  // Multiple individually chosen targets follow the same universal rule.
  window.IRON_PIT_BROWSER_RESOURCES = {
    available: () => true, spend: () => null,
  };
  window.IRON_PIT_BROWSER_FORMATION = { saveDistance: () => 5 };
  load("browser-multi-save-provider.js");
  const M = window.IRON_PIT_BROWSER_MULTI_SAVE_PROVIDER;
  jumper.state.action_available = true;
  const multi = { ...action, area: null, maxTargets: 2 };
  rolled.length = 0;
  calls.length = 0;
  const multiResult = M.resolve(50, 1, jumper, field, multi, targets);
  assert.equal(multiResult.events.length, 2);
  assert.deepEqual(rolled, [[1, 6], [1, 8]]);
  assert.deepEqual(calls.map((item) => item.rolls), [
    [[6], [8]], [[6], [8]],
  ]);
}

console.log("Multi-target shared typed-save damage parity passed.");

// Run source-neutral multi-target validation parity with the existing browser CI gate.
require("./browser-save-target-cap-parity.test.cjs");

// Source-neutral area placement must not treat immune creatures as legal targets.
{
  const caster = member("monster:renamed-source", "monsters", 1, 1);
  const legal = member("hero:eligible", "heroes", 2, 1);
  const immune = member("hero:immune", "heroes", 3, 1);
  const areaAction = {
    ...action, id: "renamed-source", name: "Arbitrary Homebrew Effect",
    resourceId: "renamed-source", resourceCost: 1,
  };
  caster.state.template.saving_throw_actions = [areaAction];
  caster.state.resources["renamed-source"] = 1;
  const mixed = { heroes: [legal, immune], monsters: [caster],
    map_definition: { width_squares: 10, height_squares: 10 } };
  const originalLegal = window.IRON_PIT_BROWSER_SAVES.legalAction;
  window.IRON_PIT_BROWSER_SAVES.legalAction = (_effect, target) => target.combatant_id !== "hero:immune";
  try {
    const selected = A.choose(caster, mixed);
    assert.ok(selected);
    assert.deepEqual(selected.placement.targetIds, ["hero:eligible"]);
    const forged = { ...selected, placement: { ...selected.placement, targetIds: ["hero:immune"] } };
    assert.throws(() => A.resolve(60, 1, caster, mixed, forged), /stale or illegal area placement/);
    const empty = { ...selected, placement: { ...selected.placement, targetIds: [] } };
    assert.throws(() => A.resolve(60, 1, caster, mixed, empty), /stale or illegal area placement/);
    assert.equal(caster.state.action_available, true);
    assert.equal(caster.state.resources["renamed-source"], 1);
    const outcome = A.resolve(60, 1, caster, mixed, selected);
    assert.deepEqual(outcome.events.map((event) => event.target_id), ["hero:eligible"]);
    assert.equal(caster.state.resources["renamed-source"], 0);
    assert.equal(caster.state.action_available, false);
  } finally {
    window.IRON_PIT_BROWSER_SAVES.legalAction = originalLegal;
  }
}


// Source-neutral multi-target RAW: a printed 'all other creatures' Action affects
// eligible allies as well as foes, without including its source.
{
  const source = member("mob:source", "monsters", 1, 1);
  const ally = member("mob:living-ally", "monsters", 2, 1);
  const foe = member("hero:foe", "heroes", 3, 1);
  const effect = {
    id: "arbitrary-wave", name: "Renamed Homebrew Wave",
    actionCost: "action", targetScope: "all-other-creatures",
    saveAbility: "constitution", dc: 13, range: 0,
    area: { shape: "emanation", origin: "self", radius_ft: 30 },
  };
  source.state.template.saving_throw_actions = [effect];
  const arena = { heroes: [foe], monsters: [source, ally],
    map_definition: { width_squares: 10, height_squares: 10 } };
  calls.length = 0;
  const selection = A.choose(source, arena);
  assert.ok(selection, "Generic all-creatures save should be selectable");
  assert.deepEqual(new Set(selection.placement.targetIds), new Set(["hero:foe", "mob:living-ally"]));
  const result = A.resolve(200, 1, source, arena, selection);
  assert.deepEqual(new Set(result.events.map(row => row.target_id)),
    new Set(["hero:foe", "mob:living-ally"]));
  assert.ok(!calls.some(item => item.target === source.combatant_id));
  assert.equal(source.state.action_available, false);

  // No hostile creatures need be in range when the source affects its friends.
  source.state.action_available = true;
  calls.length = 0;
  const alliesOnly = { ...arena, heroes: [] };
  const onlyFriends = A.choose(source, alliesOnly);
  assert.ok(onlyFriends);
  assert.deepEqual(onlyFriends.placement.targetIds, ["mob:living-ally"]);
  A.resolve(220, 1, source, alliesOnly, onlyFriends);
  assert.deepEqual(calls.map(row => row.target), ["mob:living-ally"]);

  // Existing source cards still target enemies unless they opt in explicitly.
  source.state.action_available = true;
  source.state.template.saving_throw_actions = [{ ...effect, targetScope: "enemies" }];
  const oldRules = A.choose(source, arena);
  assert.ok(oldRules);
  assert.deepEqual(oldRules.placement.targetIds, ["hero:foe"]);
  const forged = { ...oldRules,
    placement: { ...oldRules.placement, targetIds: ["mob:living-ally"] } };
  assert.throws(() => A.resolve(240, 1, source, arena, forged), /stale or illegal/);
  assert.equal(source.state.action_available, true);
}
console.log("All-other-creatures area-save friendly-fire parity passed.");


{
// Source-declared Wail eligibility: allies die to a failed save elsewhere in the
// shared zero-HP primitive, but are never exempted by allegiance here.
  const source = member("banshee", "monsters", 1, 1);
  const friend = member("living-friend", "monsters", 2, 1);
  const construct = member("construct-friend", "monsters", 3, 1);
  const undead = member("undead-friend", "monsters", 4, 1);
  const hero = member("hero", "heroes", 5, 1);
  const deaf = member("deaf", "heroes", 6, 1);
  source.state.template.creature_type = "undead";
  friend.state.template.creature_type = "humanoid";
  construct.state.template.creature_type = "construct";
  undead.state.template.creature_type = "undead";
  hero.state.template.creature_type = "humanoid";
  deaf.state.template.creature_type = "humanoid";
  deaf.state.active_effect_ids = ["deafened"];
  const wail = {
    id: "source-wail", name: "Wail (1/Day)", targetScope: "all-other-creatures",
    actionCost: "action", saveAbility: "constitution", dc: 13, range: 30,
    area: { shape: "emanation", origin: "self", radius_ft: 30 },
    damageDiceCount: 3, damageDiceSize: 6, damageType: "psychic",
    failureSetsZeroHp: true, damageOnlyOnSuccess: true,
    excludedTargetCreatureTypes: ["construct", "undead"],
    requiresTargetHearing: true, prohibitedEnvironmentContextId: "sunlight",
    resourceId: "source-wail", resourceCost: 1,
  };
  source.state.template.saving_throw_actions = [wail];
  source.state.resources["source-wail"] = 1;
  const scene = {
    heroes: [hero, deaf], monsters: [source, friend, construct, undead],
    map_definition: { width_squares: 10, height_squares: 10 },
  };
  let sunlight = false;
  window.IRON_PIT_BROWSER_ENVIRONMENT_CONTEXTS = {
    inside: (_actor, _setup, contextId) => contextId === "sunlight" && sunlight,
  };
  const original = window.IRON_PIT_BROWSER_SAVES.legalAction;
  window.IRON_PIT_BROWSER_SAVES.legalAction = (action, target) =>
    !(action.excludedTargetCreatureTypes || []).includes(target.state.template.creature_type)
    && !(action.requiresTargetHearing && (target.state.active_effect_ids || []).includes("deafened"));
  try {
    const legal = A.choose(source, scene);
    assert.ok(legal);
    assert.deepEqual(new Set(legal.placement.targetIds), new Set(["hero", "living-friend"]));
    sunlight = true;
    assert.equal(A.choose(source, scene), null, "Sunlight prohibits Wail before spending resources");
    assert.throws(() => A.resolve(300, 1, source, scene, legal), /prohibited/);
    assert.equal(source.state.resources["source-wail"], 1);
    sunlight = false;
    const outcome = A.resolve(300, 1, source, scene, legal);
    assert.equal(outcome.events.length, 2);
    assert.deepEqual(new Set(outcome.events.map(e => e.target_id)), new Set(["hero", "living-friend"]));
    assert.equal(source.state.resources["source-wail"], 0);
    assert.equal(A.choose(source, scene), null, "Spent Wail cannot recur in same fight");
  } finally {
    window.IRON_PIT_BROWSER_SAVES.legalAction = original;
    delete window.IRON_PIT_BROWSER_ENVIRONMENT_CONTEXTS;
  }
}
console.log("2014 source Wail eligibility, sunlight and friendly-fire parity passed.");
