"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-dice.js", "browser-monsters.js", "browser-monsters-expansion.js",
  "browser-condition-rules.js", "browser-action-economy.js", "browser-grapple.js",
  "browser-timed-conditions.js", "browser-state.js", "browser-rage.js",
  "browser-rolls.js", "browser-zero-hp.js", "browser-attack.js", "browser-target-state.js", "browser-formation.js", "browser-multiattack.js", "browser-saves.js",
]) load(file);

const queuedDice = (values, fallback = 10) => {
  const queue = [...values];
  const roll = (sides) => ((queue.length ? queue.shift() : fallback) - 1) % sides + 1;
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
};
const S = window.IRON_PIT_BROWSER_STATE;
const A = window.IRON_PIT_BROWSER_ATTACK;
const M = window.IRON_PIT_BROWSER_MULTIATTACK;
const T = window.IRON_PIT_BROWSER_TARGET_STATE;
const SV = window.IRON_PIT_BROWSER_SAVES;
const monsters = window.IRON_PIT_BROWSER_MONSTERS;
const member = (id, side, template, position) => ({
  combatant_id: id, side, position_ft: position, state: S.buildState(structuredClone(template)),
});
const targetTemplate = {
  id: "target", name: "Target", kind: "character", size: "medium", armor_class: 10,
  max_hp: 100, speed_ft: 30, initiative_bonus: 0, attacks: [], resources: {}, traits: [],
};

{
  const goblin = monsters["srd-goblin-minion"];
  const kobold = monsters["srd-kobold-warrior"];
  assert.deepEqual(goblin.attacks.map((profile) => profile.kind), ["melee", "ranged"]);
  assert.deepEqual([goblin.attacks[1].normal, goblin.attacks[1].long], [20, 60]);
  assert.equal(kobold.traits.includes("pack-tactics"), true);
  const one = member("kobold-1", "monsters", kobold, 5);
  const two = member("kobold-2", "monsters", kobold, 5);
  const hero = member("hero", "heroes", targetTemplate, 0);
  assert.equal(S.packTactics(one, { heroes: [hero], monsters: [one, two] }), true);
  two.state.current_hp = 0; two.state.is_alive = false; two.state.is_dead = true;
  assert.equal(S.packTactics(one, { heroes: [hero], monsters: [one, two] }), false);
}

{
  const hobgoblin = monsters["srd-hobgoblin-warrior"];
  const bow = hobgoblin.attacks.find((profile) => profile.id === "hobgoblin-longbow");
  const attacker = member("hob", "monsters", hobgoblin, 30);
  const target = member("hero", "heroes", targetTemplate, 0);
  window.IRON_PIT_DICE = queuedDice([15, 5, 1, 2, 3]);
  const event = A.resolveAttack(1, 1, attacker, target, bow, 30);
  assert.equal(event.hit, true);
  assert.deepEqual(event.damage_components.map((part) => part.damage_type), ["piercing", "poison"]);
  assert.deepEqual(event.damage_components.map((part) => part.total), [6, 6]);
}

{
  const hippogriff = monsters["srd-hippogriff"];
  const attacker = member("hippogriff", "monsters", hippogriff, 5);
  const target = member("hero", "heroes", targetTemplate, 0);
  const setup = { heroes: [target], monsters: [attacker] };
  S.beginTurn(attacker.state);
  window.IRON_PIT_DICE = queuedDice([15, 4, 15, 5]);
  const result = M.resolveAttackAction(1, 1, attacker, setup);
  assert.equal(hippogriff.speed_ft, 60);
  assert.equal(result.events.filter((event) => event.event_type === "attack").length, 2);
  assert.deepEqual(result.events.map((event) => event.weapon_id), ["hippogriff-rend", "hippogriff-rend"]);
}

{
  const attack = { id: "claw", name: "Claw", kind: "melee", bonus: 0, diceCount: 1, diceSize: 4, damageBonus: 0, damageType: "slashing", reach: 5 };
  const frenzyTemplate = { ...targetTemplate, id: "frenzy", name: "Frenzy", kind: "monster", armor_class: 10, max_hp: 20,
    attacks: [attack], primary_attack_id: "claw", traits: ["target-missing-hp-attack-advantage"] };
  const attacker = member("frenzy", "monsters", frenzyTemplate, 5);
  const target = member("hero", "heroes", targetTemplate, 0);
  assert.equal(T.attackAdvantage(attacker, target), 0);
  target.state.current_hp = 99;
  assert.equal(T.attackAdvantage(attacker, target), 1);
  target.state.max_hp_reduction = 1;
  assert.equal(T.attackAdvantage(attacker, target), 0, "effective max HP prevents false injured state");
  target.state.max_hp_reduction = 0;
  window.IRON_PIT_DICE = queuedDice([5, 15, 3]);
  const event = A.resolveAttack(1, 1, attacker, target, attack, 5, { spendAction: false });
  assert.equal(event.attack_roll.mode, "advantage");
  assert.equal(event.hit, true, "injured target Advantage selects the higher d20");
}

{
  const attack = { id: "axe", name: "Axe", kind: "melee", bonus: 0, diceCount: 1, diceSize: 4, damageBonus: 0, damageType: "slashing", reach: 5 };
  const bloodiedTemplate = { ...targetTemplate, id: "bloodied", name: "Bloodied", kind: "monster", armor_class: 10, max_hp: 20,
    saving_throw_bonuses: { wisdom: 0, dexterity: 0 }, attacks: [attack], primary_attack_id: "axe", traits: ["bloodied-attack-save-advantage"] };
  const attacker = member("bloodied", "monsters", bloodiedTemplate, 5);
  const target = member("hero", "heroes", targetTemplate, 0);
  attacker.state.current_hp = 10;
  assert.equal(T.isBloodied(attacker.state), true);
  assert.equal(T.attackAdvantage(attacker, target), 1);
  assert.equal(SV.saveMode(attacker.state, "wisdom"), "advantage");
  attacker.state.active_effect_ids.push("restrained");
  assert.equal(SV.saveMode(attacker.state, "dexterity"), "normal", "Bloodied Advantage cancels save Disadvantage");
  attacker.state.max_hp_reduction = 1;
  assert.equal(T.isBloodied(attacker.state), false, "Bloodied threshold follows effective max HP");
}

console.log("Browser expansion monster regressions passed.");
