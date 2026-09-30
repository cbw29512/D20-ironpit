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
