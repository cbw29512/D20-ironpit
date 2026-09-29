"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = globalThis;

const load = (name) => vm.runInThisContext(
  fs.readFileSync(`frontend/${name}`, "utf8"),
  { filename: name },
);

window.IRON_PIT_BROWSER_STATE = {
  distance: (a, b) => Math.abs(a.position_ft - b.position_ft),
};
window.IRON_PIT_BROWSER_RESOURCES = {
  available: (state, id, cost = 1) => (state.resources[id] || 0) >= cost,
  spend: (state, id, cost = 1) => {
    if ((state.resources[id] || 0) < cost) throw new Error("resource unavailable");
    state.resources[id] -= cost;
    return state.resources[id];
  },
};

function member(id, side, position, fate = false) {
  return {
    combatant_id: id,
    side,
    position_ft: position,
    state: {
      is_alive: true,
      is_dead: false,
      resources: fate ? { "boon-of-fate": 1 } : {},
      active_effect_ids: [],
      active_d20_bonus_dice: [],
      template: {
        name: id,
        saving_throw_bonuses: { wisdom: 2 },
        ability_scores: { wisdom: 20 },
        failed_d20_test_override_grants: [],
        resource_backed_d20_bonus_dice: [],
        resource_backed_d20_outcome_adjustments: fate ? [{
          source_id: "boon-of-fate",
          source_name: "Boon of Fate",
          resource_id: "boon-of-fate",
          resource_cost: 1,
          dice_count: 2,
          dice_size: 4,
          range_ft: 60,
          test_kinds: ["attack", "saving_throw", "ability_check"],
          can_add: true,
          can_subtract: true,
        }] : [],
      },
    },
  };
}

function roll(total, natural = 10) {
  return {
    notation: "1d20+2",
    rolls: [natural],
    selected_roll: natural,
    modifier: 2,
    total,
    mode: "normal",
    revisions: [],
  };
}

load("browser-d20-outcome-adjustments.js");
const O = window.IRON_PIT_BROWSER_D20_OUTCOME_ADJUSTMENTS;

{
  const source = member("source", "heroes", 0, true);
  const ally = member("ally", "heroes", 20);
  const enemy = member("enemy", "monsters", 20);
  const setup = { heroes: [source, ally], monsters: [enemy] };
  const queue = [2, 2];
  window.IRON_PIT_DICE = { roll: () => queue.shift() };
  const result = O.applyIfUseful(ally, setup, "saving_throw", roll(12), 15);
  assert.equal(result.direction, "add");
  assert.equal(result.roll.total, 16);
  assert.equal(result.roll.revisions.at(-1).kind, "roll_adjustment");
  assert.equal(source.state.resources["boon-of-fate"], 0);
}

{
  const source = member("source", "heroes", 0, true);
  const enemy = member("enemy", "monsters", 20);
  const setup = { heroes: [source], monsters: [enemy] };
  const queue = [2, 1];
  window.IRON_PIT_DICE = { roll: () => queue.shift() };
  const result = O.applyIfUseful(enemy, setup, "ability_check", roll(16), 15);
  assert.equal(result.direction, "subtract");
  assert.equal(result.roll.total, 13);
  assert.equal(source.state.resources["boon-of-fate"], 0);
}

{
  const source = member("source", "heroes", 0, true);
  const ally = member("ally", "heroes", 80);
  const setup = { heroes: [source, ally], monsters: [] };
  window.IRON_PIT_DICE = { roll: () => 4 };
  const result = O.applyIfUseful(ally, setup, "saving_throw", roll(12), 15);
  assert.equal(result.featureId, null);
  assert.equal(source.state.resources["boon-of-fate"], 1);
}

{
  const source = member("source", "heroes", 0, true);
  const enemy = member("enemy", "monsters", 20);
  const setup = { heroes: [source], monsters: [enemy] };
  window.IRON_PIT_DICE = { roll: () => 4 };
  const result = O.applyIfUseful(enemy, setup, "attack", roll(22, 20), 15, 20);
  assert.equal(result.featureId, null);
  assert.equal(source.state.resources["boon-of-fate"], 1);
}

window.IRON_PIT_BROWSER_REACTIONS = {
  parryHit: (_defender, _attack, _roll, hit) => ({ hit, used: false }),
};
window.IRON_PIT_BROWSER_D20_TEST_OVERRIDE = {
  apply: (_state, r) => ({ roll: r, featureId: null, sourceName: null }),
};
window.IRON_PIT_BROWSER_MISS_TO_HIT_OVERRIDE = {
  apply: (_state, hit) => ({ hit, featureId: null, sourceName: null }),
};
load("browser-attack-outcome.js");

{
  const source = member("source", "heroes", 0, true);
  const attacker = member("attacker", "monsters", 20);
  const defender = member("defender", "heroes", 20);
  const setup = { heroes: [source, defender], monsters: [attacker] };
  const queue = [2, 1];
  window.IRON_PIT_DICE = { roll: () => queue.shift() };
  const outcome = window.IRON_PIT_BROWSER_ATTACK_OUTCOME.resolveD20(
    attacker.state,
    defender.state,
    { id: "claw" },
    roll(16),
    15,
    attacker,
    setup,
  );
  assert.equal(outcome.hit, false);
  assert.equal(outcome.adjustment.featureId, "boon-of-fate");
  assert.equal(outcome.roll.total, 13);
}

window.IRON_PIT_BROWSER_ROLLS = {
  d20: (modifier) => ({
    notation: `1d20+${modifier}`,
    rolls: [10],
    selected_roll: 10,
    modifier,
    total: 10 + modifier,
    mode: "normal",
    revisions: [],
  }),
  modeFromSources: () => "normal",
};
window.IRON_PIT_BROWSER_BARBARIAN2 = { dangerSenseAdvantage: () => 0 };
window.IRON_PIT_BROWSER_DODGE = { dexSaveAdvantageSources: () => 0 };
window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS = {
  saveAdvantage: () => 0,
  saveAdvantageSourceNames: () => [],
  saveDisadvantage: () => 0,
  consumeSavingThrowModifiers: () => {},
};
window.IRON_PIT_BROWSER_MODIFIERS = {
  applyD20Bonus: (_state, _kind, r) => r,
  savingThrowFlat: () => 0,
};
window.IRON_PIT_BROWSER_EXHAUSTION = { saveDisadvantage: () => 0 };
window.IRON_PIT_BROWSER_FAILED_SAVE_REROLL = {
  apply: (_state, r) => ({ roll: r, featureId: null, sourceName: null }),
};
window.IRON_PIT_BROWSER_CONDITION_RULES = { autoFailStrDex: () => false };
load("browser-saving-throws.js");

{
  const source = member("source", "heroes", 0, true);
  const enemy = member("enemy", "monsters", 20);
  enemy.state.template.saving_throw_bonuses.wisdom = 6;
  const setup = { heroes: [source], monsters: [enemy] };
  const queue = [2, 1];
  window.IRON_PIT_DICE = { roll: () => queue.shift() };
  const result = window.IRON_PIT_BROWSER_SAVING_THROWS.resolveSavingThrow(
    enemy.state,
    "wisdom",
    15,
    { encounterRoller: enemy, setup },
  );
  assert.equal(result.succeeded, false);
  assert.equal(result.roll.total, 13);
  assert.equal(source.state.resources["boon-of-fate"], 0);
}

window.IRON_PIT_BROWSER_D20_BONUS_DICE = null;
load("browser-ability-checks.js");

{
  const source = member("source", "heroes", 0, true);
  const ally = member("ally", "heroes", 20);
  const setup = { heroes: [source, ally], monsters: [] };
  const queue = [2, 2];
  window.IRON_PIT_DICE = { roll: () => queue.shift() };
  const result = window.IRON_PIT_BROWSER_ABILITY_CHECKS.resolve(
    ally.state,
    "wisdom",
    roll(12),
    15,
    { roller: ally, setup },
  );
  assert.equal(result.succeeded, true);
  assert.equal(result.roll.total, 16);
  assert.equal(source.state.resources["boon-of-fate"], 0);
}

console.log("Browser D20 outcome adjustment regressions passed.");
