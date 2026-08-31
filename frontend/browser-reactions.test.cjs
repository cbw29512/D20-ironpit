"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters.js", "browser-monsters-beast2.js",
  "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-grapple.js", "browser-state.js", "browser-rage.js", "browser-rolls.js", "browser-timed-conditions.js",
  "browser-attack.js", "browser-reactions.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const X = window.IRON_PIT_BROWSER_REACTIONS;
const heroTemplate = () => structuredClone(window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"]);
const monsterTemplate = (id) => structuredClone(window.IRON_PIT_BROWSER_MONSTERS[id]);
const member = (id, side, template, position) => ({ combatant_id: id, side, position_ft: position, state: S.buildState(template) });
const dice = () => { window.IRON_PIT_DICE = { roll: (sides) => sides === 20 ? 19 : 1, rollMany: (count, sides) => Array.from({ length: count }, () => sides === 20 ? 19 : 1) }; };

function setup(monsterId = "srd-commoner") {
  const hero = member("hero-1", "heroes", heroTemplate(), 5);
  const monster = member("monster-1", "monsters", monsterTemplate(monsterId), 0);
  return { hero, monster, fight: { heroes: [hero], monsters: [monster] } };
}

{
  dice(); const { hero, monster, fight } = setup();
  const event = X.resolveOpportunityAttack(1, 1, monster, hero, fight, 5, 10, "speed");
  assert.ok(event); assert.equal(event.feature_id, "opportunity-attack"); assert.equal(event.event_type, "attack");
  assert.equal(monster.state.reaction_available, false); assert.equal(monster.state.action_available, true);
  assert.equal(X.resolveOpportunityAttack(2, 1, monster, hero, fight, 5, 10, "speed"), null);
  S.beginTurn(monster.state); assert.equal(monster.state.reaction_available, true);
}
{
  for (const [source, disengaged] of [["speed", true], ["teleport", false], ["forced", false]]) {
    dice(); const { hero, monster, fight } = setup();
    assert.equal(X.resolveOpportunityAttack(1, 1, monster, hero, fight, 5, 10, source, { disengaged }), null);
    assert.equal(monster.state.reaction_available, true);
  }
}
{
  dice(); const { hero, monster, fight } = setup(); monster.state.active_effect_ids.push("stunned");
  assert.equal(X.resolveOpportunityAttack(1, 1, monster, hero, fight, 5, 10, "speed"), null);
}
{
  dice(); const { hero, monster, fight } = setup("srd-plesiosaurus");
  const attack = monster.state.template.attacks.find((item) => item.kind === "melee"); assert.equal(attack.reach, 10);
  assert.equal(X.resolveOpportunityAttack(1, 1, monster, hero, fight, 5, 10, "speed"), null);
  assert.ok(X.resolveOpportunityAttack(1, 1, monster, hero, fight, 10, 15, "speed"));
}
{
  for (const source of ["action", "bonus_action", "reaction"]) {
    dice(); const { hero, monster, fight } = setup();
    assert.ok(X.resolveOpportunityAttack(1, 1, monster, hero, fight, 5, 10, source));
  }
}
{
  const defender = S.buildState(heroTemplate()); defender.template.parry_reaction = { ac_bonus: 2 };
  const attack = monsterTemplate("srd-commoner").attacks[0]; const total = defender.template.armor_class + 1;
  assert.deepEqual(X.parryHit(defender, attack, { selected_roll: 12, total }, true), { hit: false, used: true });
  assert.equal(defender.reaction_available, false);
}
{
  const defender = S.buildState(heroTemplate()); defender.template.parry_reaction = { ac_bonus: 2 };
  const melee = monsterTemplate("srd-commoner").attacks[0]; const ranged = { ...melee, kind: "ranged" };
  const total = defender.template.armor_class + 2;
  assert.deepEqual(X.parryHit(defender, melee, { selected_roll: 12, total }, true), { hit: true, used: false });
  assert.deepEqual(X.parryHit(defender, ranged, { selected_roll: 12, total: defender.template.armor_class }, true), { hit: true, used: false });
  assert.deepEqual(X.parryHit(defender, melee, { selected_roll: 20, total: 99 }, true), { hit: true, used: false });
  assert.equal(defender.reaction_available, true);
}
console.log("Browser Opportunity Attack and Parry Reaction regressions passed.");
