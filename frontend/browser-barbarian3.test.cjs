"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const htmlPath of [path.join(__dirname, "index.html"), path.join(__dirname, "..", "index.html")]) {
  const html = fs.readFileSync(htmlPath, "utf8");
  assert.match(html, /<script src="browser-barbarian3\.js"><\/script>/, `${htmlPath} must load Barbarian 3 runtime rules`);
}
for (const file of [
  "browser-heroes.js", "browser-monsters.js", "browser-monsters-fixed.js",
  "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-grapple.js", "browser-timed-conditions.js", "browser-barbarian2.js", "browser-state.js",
  "browser-rage.js", "browser-barbarian3.js", "browser-rolls.js", "browser-zero-hp.js", "browser-attack.js",
  "browser-formation.js", "browser-multiattack.js",
]) load(file);

function queuedDice(values, fallback = 10) {
  const queue = [...values];
  const roll = (sides) => ((queue.length ? queue.shift() : fallback) - 1) % sides + 1;
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
}

function setup() {
  const template = structuredClone(window.IRON_PIT_BROWSER_HEROES["rokhan-stonefury-l3"]);
  assert.ok(template, "Barbarian 3 must be generated as a browser-ready hero");
  const bandit = structuredClone(window.IRON_PIT_BROWSER_MONSTERS["srd-bandit"]);
  const hero = { combatant_id: "hero-1:rokhan-stonefury-l3", side: "heroes", position_ft: 5, state: window.IRON_PIT_BROWSER_STATE.buildState(template) };
  const monster = { combatant_id: "monster-1:bandit", side: "monsters", position_ft: 10, state: window.IRON_PIT_BROWSER_STATE.buildState(bandit) };
  return { template, bandit, hero, monster, setup: { heroes: [hero], monsters: [monster] } };
}

function rage(hero) {
  window.IRON_PIT_BROWSER_STATE.beginTurn(hero.state);
  assert.ok(window.IRON_PIT_BROWSER_RAGE.enter(1, 1, hero));
}

{
  const { template } = setup();
  assert.equal(template.level, 3);
  assert.equal(template.max_hp, 32);
  assert.equal(template.resources.rage, 3);
  assert.equal(template.danger_sense, true);
  assert.equal(template.reckless_attack, true);
  assert.equal(template.frenzy, true);
  assert.equal(template.attacks[0].attackAbility, "strength");
  assert.equal(template.attacks[1].attackAbility, "strength");
}

{
  const template = structuredClone(window.IRON_PIT_BROWSER_HEROES["rokhan-stonefury-l4"]);
  assert.ok(template, "Barbarian 4 must be generated as a browser-ready hero");
  assert.equal(template.level, 4);
  assert.equal(template.armor_class, 14);
  assert.equal(template.max_hp, 45);
  assert.equal(template.resources.rage, 3);
  assert.equal(template.danger_sense, true);
  assert.equal(template.reckless_attack, true);
  assert.equal(template.frenzy, true);
  assert.equal(template.saving_throw_bonuses.strength, 6);
  assert.equal(template.saving_throw_bonuses.constitution, 5);
  assert.equal(template.skill_bonuses.athletics, 6);
  assert.equal(template.attacks[0].bonus, 6);
  assert.equal(template.attacks[0].damageBonus, 4);
  assert.equal(template.attacks[1].bonus, 6);
  assert.equal(template.attacks[1].damageBonus, 4);
}

{
  const template = structuredClone(window.IRON_PIT_BROWSER_HEROES["rokhan-stonefury-l5"]);
  assert.ok(template, "Barbarian 5 must be generated as a browser-ready hero");
  assert.equal(template.level, 5);
  assert.equal(template.armor_class, 14);
  assert.equal(template.max_hp, 55);
  assert.equal(template.speed_ft, 40);
  assert.equal(template.fast_movement_bonus_ft, 10);
  assert.equal(template.resources.rage, 3);
  assert.equal(template.resources["adrenaline-rush"], 3);
  assert.equal(template.danger_sense, true);
  assert.equal(template.reckless_attack, true);
  assert.equal(template.frenzy, true);
  assert.equal(template.saving_throw_bonuses.strength, 7);
  assert.equal(template.saving_throw_bonuses.constitution, 6);
  assert.equal(template.skill_bonuses.athletics, 7);
  assert.equal(template.attacks[0].bonus, 7);
  assert.equal(template.attacks[0].damageBonus, 4);
  assert.equal(template.attacks[1].bonus, 7);
  assert.equal(template.attacks[1].damageBonus, 4);
  assert.equal(template.attack_action.slots.length, 2);
}

{
  const template = structuredClone(window.IRON_PIT_BROWSER_HEROES["rokhan-stonefury-l5"]);
  const targetTemplate = structuredClone(window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l5"]);
  const hero = { combatant_id: "hero-1:rokhan-stonefury-l5", side: "heroes", position_ft: 5, state: window.IRON_PIT_BROWSER_STATE.buildState(template) };
  const monster = { combatant_id: "monster-1:test-fighter", side: "monsters", position_ft: 10, state: window.IRON_PIT_BROWSER_STATE.buildState(targetTemplate) };
  monster.state.template.armor_class = 10;
  const arena = { heroes: [hero], monsters: [monster] };
  rage(hero);
  window.IRON_PIT_DICE = queuedDice([2, 15, 4, 8, 3, 5, 3, 14, 7]);
  const result = window.IRON_PIT_BROWSER_MULTIATTACK.resolveAttackAction(2, 1, hero, arena);
  const attacks = result.events.filter((event) => event.event_type === "attack");
  assert.equal(attacks.length, 2);
  assert.ok(attacks.every((event) => event.hit));
  assert.ok(attacks.every((event) => event.attack_roll.mode === "advantage"));
  const frenzy = attacks.flatMap((event) => event.damage_components).filter((part) => part.source === "Frenzy");
  assert.equal(frenzy.length, 1, "Extra Attack must share first-hit Frenzy state across both attacks");
  assert.deepEqual(frenzy[0].rolls, [3, 5]);
  assert.match(attacks[0].description, /uses Reckless Attack/);
  assert.doesNotMatch(attacks[1].description, /uses Reckless Attack/);
}

{
  const { template, hero, monster, setup: arena } = setup();
  rage(hero);
  window.IRON_PIT_DICE = queuedDice([2, 15, 4, 8, 3, 5]);
  const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(2, 1, hero, monster, template.attacks[0], 5, {
    setup: arena, spendAction: false, allowReckless: true, turnKey: `1:${hero.combatant_id}`,
  });
  const frenzy = event.damage_components.find((part) => part.source === "Frenzy");
  assert.ok(event.hit);
  assert.ok(frenzy, "first raging Reckless Strength hit must apply Frenzy");
  assert.equal(frenzy.notation, "2d6+0");
  assert.deepEqual(frenzy.rolls, [3, 5]);
  assert.equal(frenzy.damage_type, "slashing");
}

{
  const { template, hero, monster, setup: arena } = setup();
  rage(hero);
  const turnKey = `1:${hero.combatant_id}`;
  monster.state.template.armor_class = 99;
  window.IRON_PIT_DICE = queuedDice([2, 3]);
  const miss = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(2, 1, hero, monster, template.attacks[0], 5, {
    setup: arena, spendAction: false, allowReckless: true, turnKey,
  });
  assert.equal(miss.hit, false);
  assert.equal(miss.damage_components.length, 0);

  monster.state.template.armor_class = 10;
  window.IRON_PIT_DICE = queuedDice([15, 4, 8, 2, 6, 5]);
  const hit = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(3, 1, hero, monster, template.attacks[0], 5, {
    setup: arena, spendAction: false, allowReckless: true, turnKey,
  });
  assert.ok(hit.damage_components.some((part) => part.source === "Frenzy"), "a miss must not consume Frenzy");

  window.IRON_PIT_DICE = queuedDice([15, 7, 5]);
  const second = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(4, 1, hero, monster, template.attacks[0], 5, {
    setup: arena, spendAction: false, allowReckless: true, turnKey,
  });
  assert.ok(second.damage_components.every((part) => part.source !== "Frenzy"), "Frenzy is first-hit-only per turn");
}

{
  const { template, hero, monster, setup: arena } = setup();
  rage(hero);
  window.IRON_PIT_DICE = queuedDice([1, 20, 1, 2, 5, 6, 1, 2, 3, 4]);
  const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(2, 1, hero, monster, template.attacks[0], 5, {
    setup: arena, spendAction: false, allowReckless: true, turnKey: `1:${hero.combatant_id}`,
  });
  const frenzy = event.damage_components.find((part) => part.source === "Frenzy");
  assert.equal(event.critical, true);
  assert.equal(frenzy.notation, "4d6+0");
  assert.deepEqual(frenzy.rolls, [1, 2, 3, 4]);
}

{
  const { template, hero, monster, setup: arena } = setup();
  rage(hero);
  window.IRON_PIT_DICE = queuedDice([2, 15, 4, 8]);
  const noTurn = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(2, 1, hero, monster, template.attacks[0], 5, {
    setup: arena, spendAction: false, allowReckless: true,
  });
  assert.ok(noTurn.damage_components.every((part) => part.source !== "Frenzy"), "Frenzy must fail closed without own-turn identity");
}

console.log("Browser Barbarian 3-5 Frenzy/Extra Attack regressions passed.");
require("./browser-barbarian6.test.cjs");
