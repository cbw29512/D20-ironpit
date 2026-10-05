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
  "browser-state.js", "browser-action-economy.js", "browser-healing-policy.js",
  "browser-healing-resolution.js", "browser-healing.js",
]) load(file);

const fighter3 = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l3"];
const fighter4 = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l4"];
assert.ok(fighter3, "generated Fighter 3 card must exist");
assert.ok(fighter4, "generated Fighter 4 card must exist");

for (const fighter of [fighter3, fighter4]) {
  assert.equal(fighter.critical_hit_minimum, 19);
  assert.equal(fighter.initiative_advantage, true);
  assert.equal(fighter.athletics_advantage, true);
  assert.equal(fighter.critical_move_fraction, 0.5);
}

assert.equal(fighter4.level, 4);
assert.equal(fighter4.max_hp, 40);
assert.equal(fighter4.armor_class, 17);
assert.equal(fighter4.fighting_style, "Defense");
assert.deepEqual(fighter4.weapon_masteries, ["flail", "javelin", "spear", "longsword"]);
assert.equal(fighter4.saving_throw_bonuses.strength, 6);
assert.equal(fighter4.saving_throw_bonuses.constitution, 5);
assert.equal(fighter4.skill_bonuses.athletics, 6);
assert.equal(fighter4.resources["second-wind"], 3);
assert.equal(fighter4.resources["action-surge"], 1);
assert.equal(fighter4.resources["adrenaline-rush"], 2);
assert.equal(fighter4.resources["relentless-endurance"], 1);

const greatsword = fighter4.attacks.find((attack) => attack.id === "karnok-greatsword");
const shortbow = fighter4.attacks.find((attack) => attack.id === "karnok-shortbow");
assert.ok(greatsword);
assert.ok(shortbow);
assert.equal(greatsword.bonus, 6);
assert.equal(greatsword.damageBonus, 4);
assert.equal(shortbow.bonus, 3);
assert.equal(shortbow.damageBonus, 1);

const secondWind = (fighter4.healingActions || []).find((action) => action.id === "second-wind");
assert.ok(secondWind, "generated Fighter 4 must declare Second Wind as healing data");
assert.equal(secondWind.actionCost, "bonus_action");
assert.equal(secondWind.targetMode, "self");
assert.equal(secondWind.diceCount, 1);
assert.equal(secondWind.diceSize, 10);
assert.equal(secondWind.healingBonus, 4);
assert.equal(secondWind.resourceId, "second-wind");

window.IRON_PIT_DICE = { roll: () => 5 };
const member = {
  combatant_id: "hero-1", side: "heroes", position_ft: 0,
  state: window.IRON_PIT_BROWSER_STATE.buildState(structuredClone(fighter4)),
};
member.state.current_hp = 20;
const setup = { heroes: [member], monsters: [] };
const choice = window.IRON_PIT_BROWSER_HEALING.chooseAction(member, setup, "1:hero-1");
assert.ok(choice, "bloodied Fighter 4 should select Second Wind");
assert.equal(choice.action.id, "second-wind");
const wind = window.IRON_PIT_BROWSER_HEALING.resolve(
  1, 1, member, member, choice.action, "1:hero-1",
);
assert.equal(wind.healing_roll.notation, "1d10+4");
assert.equal(wind.healing_roll.modifier, 4);
assert.equal(wind.healing_roll.total, 9);
assert.equal(member.state.current_hp, 29);
assert.equal(member.state.resources["second-wind"], 2);
assert.equal(member.state.bonus_action_available, false);

console.log("Generated browser Fighter 4 regressions passed.");
