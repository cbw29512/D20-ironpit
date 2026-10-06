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
  "browser-heroes.js", "browser-condition-immunity.js", "browser-condition-rules.js",
  "browser-action-economy.js", "browser-grapple.js", "browser-state.js",
  "browser-rolls.js", "browser-zero-hp.js", "browser-ability-hooks.js", "browser-attack-outcome.js", "browser-attack.js", "browser-saving-throws.js", "browser-saves.js", "browser-charge.js",
  "browser-formation.js", "browser-multiattack-choices.js", "browser-multiattack.js", "browser-healing-policy.js", "browser-healing-resolution.js", "browser-healing.js",
  "browser-main-action-profiles.js", "browser-main-action-selection.js", "browser-main-action-providers.js", "browser-action-surge.js",
  "browser-bonus-action-follow-up.js", "browser-support.js",
]) load(file);

const fighter = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l5"];
assert.ok(fighter, "generated Fighter 5 card must exist");
assert.equal(fighter.level, 5);
assert.equal(fighter.max_hp, 49);
assert.equal(fighter.armor_class, 17);
assert.equal(fighter.fighting_style, "Defense");
assert.equal(fighter.critical_hit_minimum, 19);
assert.equal(fighter.initiative_advantage, true);
assert.equal(fighter.athletics_advantage, true);
assert.equal(fighter.critical_move_fraction, 0.5);
assert.deepEqual(fighter.bonus_action_follow_up_movement_grants, [{
  source_id: "tactical-shift",
  source_name: "Tactical Shift",
  required_trigger_ids: ["second-wind"],
  speed_fraction: 0.5,
  desired_distance_ft: 5,
  provokes_opportunity_attacks: false,
}]);
assert.deepEqual(fighter.weapon_masteries, ["flail", "javelin", "spear", "longsword"]);
assert.equal(fighter.saving_throw_bonuses.strength, 7);
assert.equal(fighter.saving_throw_bonuses.constitution, 6);
assert.equal(fighter.skill_bonuses.athletics, 7);
assert.deepEqual(fighter.resources, {
  "second-wind": 3,
  "action-surge": 1,
  "adrenaline-rush": 3,
  "relentless-endurance": 1,
});

const greatsword = fighter.attacks.find((attack) => attack.id === "karnok-greatsword");
const shortbow = fighter.attacks.find((attack) => attack.id === "karnok-shortbow");
assert.ok(greatsword);
assert.ok(shortbow);
assert.equal(greatsword.bonus, 8);
assert.equal(greatsword.damageBonus, 5);
assert.equal(shortbow.bonus, 5);
assert.equal(shortbow.damageBonus, 2);
assert.equal(fighter.attack_action.id, "extra-attack");
assert.deepEqual(fighter.attack_action.slots, [
  { attackIds: ["karnok-greatsword", "karnok-shortbow"], saveActionIds: [] },
  { attackIds: ["karnok-greatsword", "karnok-shortbow"], saveActionIds: [] },
]);

const S = window.IRON_PIT_BROWSER_STATE;
const G = window.IRON_PIT_BROWSER_GRAPPLE;
const member = (id, side, template, position) => ({
  combatant_id: id, side, position_ft: position, state: S.buildState(structuredClone(template)),
});
const targetTemplate = {
  id: "test-target", name: "Test Target", kind: "monster", size: "medium",
  armor_class: 30, max_hp: 100, speed_ft: 30, traits: [], attacks: [], resources: {},
};

{
  const hero = member("hero-shift", "heroes", fighter, 0);
  const target = member("monster-shift", "monsters", targetTemplate, 35);
  const setup = { heroes: [hero], monsters: [target] };
  hero.state.current_hp = 20;
  hero.state.movement_remaining_ft = 30;
  window.IRON_PIT_DICE = { roll: () => 5, rollMany: (count) => Array(count).fill(5) };

  let movementOptions = null;
  window.IRON_PIT_BROWSER_ACTIVATION_MOVEMENT = {
    resolve(sequence, round, mover, _setup, options) {
      movementOptions = options;
      mover.position_ft = 15;
      return {
        events: [{
          sequence, round_number: round, event_type: "movement",
          actor_id: mover.combatant_id, movement_ft: 15, description: "moves 15 feet.",
        }],
        sequence: sequence + 1,
      };
    },
  };

  const support = window.IRON_PIT_BROWSER_SUPPORT.resolve(1, 1, hero, setup, "1:hero-shift");
  const wind = support.events.find((event) => event.feature_id === "second-wind");
  const shift = support.events.find((event) => event.feature_id === "tactical-shift");
  assert.ok(wind, "support must resolve Second Wind through universal healing");
  assert.ok(shift, "Second Wind must trigger semantic Tactical Shift movement");
  assert.equal(wind.healing_roll.notation, "1d10+5");
  assert.equal(wind.healing_roll.total, 10);
  assert.equal(hero.state.current_hp, 30);
  assert.equal(hero.state.resources["second-wind"], 2);
  assert.equal(hero.state.bonus_action_available, false);
  assert.equal(hero.position_ft, 15);
  assert.equal(hero.state.movement_remaining_ft, 30);
  assert.equal(movementOptions.speedFraction, 0.5);
  assert.equal(movementOptions.provokesOpportunityAttacks, false);
  assert.equal(target.state.reaction_available, true);
}

{
  const hero = member("hero-attacks", "heroes", fighter, 0);
  const target = member("monster-attacks", "monsters", targetTemplate, 5);
  const setup = { heroes: [hero], monsters: [target] };
  window.IRON_PIT_DICE = {
    roll: () => 2,
    rollMany: (count) => Array(count).fill(2),
  };

  const normal = window.IRON_PIT_BROWSER_MULTIATTACK.resolveAttackAction(1, 1, hero, setup);
  assert.equal(normal.events.filter((event) => event.event_type === "attack").length, 2);
  assert.equal(hero.state.action_available, false);

  const surged = window.IRON_PIT_BROWSER_ACTION_SURGE.resolveAttack(normal.sequence, 1, hero, setup, "1:hero-attacks");
  assert.ok(surged);
  assert.equal(surged.events.filter((event) => event.feature_id === "action-surge").length, 1);
  assert.equal(surged.events.filter((event) => event.event_type === "attack").length, 2);
  assert.equal(hero.state.resources["action-surge"], 0);
  assert.equal(hero.state.action_available, false);
}

console.log("Generated browser Fighter 5 regressions passed.");
require("./browser-fighter6.test.cjs");
