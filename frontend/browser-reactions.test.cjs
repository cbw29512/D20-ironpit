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
const A = window.IRON_PIT_BROWSER_ATTACK;
const heroTemplate = () => structuredClone(window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"]);
const monsterTemplate = (id) => structuredClone(window.IRON_PIT_BROWSER_MONSTERS[id]);
const member = (id, side, template, position) => ({ combatant_id: id, side, position_ft: position, state: S.buildState(template) });
const dice = () => { window.IRON_PIT_DICE = { roll: (sides) => sides === 20 ? 19 : 1, rollMany: (count, sides) => Array.from({ length: count }, () => sides === 20 ? 19 : 1) }; };
const fixedDice = (values) => {
  const queue = [...values];
  window.IRON_PIT_DICE = {
    roll: () => queue.shift(),
    rollMany: (count) => Array.from({ length: count }, () => queue.shift()),
  };
};

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
{
  const attacker = member("archer-1", "heroes", monsterTemplate("srd-goblin-warrior"), 0);
  const bossTemplate = monsterTemplate("srd-goblin-warrior");
  bossTemplate.name = "Goblin Boss"; bossTemplate.armor_class = 17; bossTemplate.max_hp = 21;
  bossTemplate.redirect_attack_reaction = { ally_range_ft: 5, ally_max_size: "medium" };
  const boss = member("boss-1", "monsters", bossTemplate, 20);
  const ally = member("ally-1", "monsters", monsterTemplate("srd-goblin-warrior"), 25);
  const fight = { heroes: [attacker], monsters: [boss, ally] };
  const ranged = attacker.state.template.attacks.find((attack) => attack.kind === "ranged");
  const bossHp = boss.state.current_hp, allyHp = ally.state.current_hp;
  fixedDice([11, 1]);
  const event = A.resolveAttack(1, 1, attacker, boss, ranged, 20, { setup: fight });
  assert.equal(event.attack_roll.total, 15); assert.equal(event.target_id, ally.combatant_id); assert.equal(event.hit, true);
  assert.equal(boss.state.current_hp, bossHp); assert.ok(ally.state.current_hp < allyHp);
  assert.equal(boss.state.reaction_available, false); assert.deepEqual([boss.position_ft, ally.position_ft], [25, 20]);
  assert.match(event.description, /uses Redirect Attack/);
}
{
  const bossTemplate = monsterTemplate("srd-goblin-warrior");
  bossTemplate.redirect_attack_reaction = { ally_range_ft: 5, ally_max_size: "medium" };
  const boss = member("boss-1", "monsters", bossTemplate, 20);
  const ally = member("ally-1", "monsters", monsterTemplate("srd-goblin-warrior"), 25);
  const fight = { heroes: [member("hero-1", "heroes", heroTemplate(), 0)], monsters: [boss, ally] };
  boss.state.active_effect_ids.push("blinded");
  assert.equal(X.redirectAttack(boss, fight), null); assert.equal(boss.state.reaction_available, true);
}
console.log("Browser Opportunity Attack, Parry, and Redirect Attack regressions passed.");
