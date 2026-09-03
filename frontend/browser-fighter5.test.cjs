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
  "browser-heroes.js", "browser-action-economy.js", "browser-grapple.js", "browser-state.js",
  "browser-rolls.js", "browser-zero-hp.js", "browser-attack.js", "browser-saves.js", "browser-charge.js",
  "browser-formation.js", "browser-multiattack.js", "browser-action-surge.js", "browser-support.js", "browser-tactical-shift.js",
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
assert.equal(fighter.tactical_shift_fraction, 0.5);
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
assert.equal(greatsword.bonus, 7);
assert.equal(greatsword.damageBonus, 4);
assert.equal(shortbow.bonus, 4);
assert.equal(shortbow.damageBonus, 1);
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

  const wind = window.IRON_PIT_BROWSER_SUPPORT.secondWind(1, 1, hero);
  assert.ok(wind);
  assert.equal(wind.healing_roll.notation, "1d10+5");
  assert.equal(wind.healing_roll.total, 10);
  assert.equal(hero.state.current_hp, 30);
  assert.equal(hero.state.resources["second-wind"], 2);
  assert.equal(hero.state.bonus_action_available, false);

  const shift = window.IRON_PIT_BROWSER_TACTICAL_SHIFT.resolve(2, 1, hero, setup);
  assert.equal(shift, null, "Tactical Shift movement is arena-neutral in fixed Pit formation");
  assert.equal(hero.position_ft, 0);
  assert.equal(hero.state.movement_remaining_ft, 30);
  assert.equal(target.state.reaction_available, true);
}

{
  const hero = member("hero-grappled", "heroes", fighter, 0);
  const target = member("monster-grappler", "monsters", targetTemplate, 35);
  const setup = { heroes: [hero], monsters: [target] };
  G.apply(hero.state, target.combatant_id, 12, 40);
  const shift = window.IRON_PIT_BROWSER_TACTICAL_SHIFT.resolve(1, 1, hero, setup);
  assert.equal(shift, null, "Tactical Shift remains arena-neutral when effective Speed is zero");
  assert.equal(hero.position_ft, 0);
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
