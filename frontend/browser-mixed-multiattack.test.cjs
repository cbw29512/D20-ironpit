"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters.js", "browser-monsters-fixed.js", "browser-monsters-beast2.js",
  "browser-monsters-batch3.js", "browser-monsters-control.js", "browser-monsters-poison.js", "browser-monsters-venom.js",
  "browser-monsters-mixed.js", "browser-grapple.js", "browser-timed-conditions.js", "browser-state.js",
  "browser-rage.js", "browser-rolls.js", "browser-attack.js", "browser-saves.js", "browser-charge.js",
  "browser-multiattack.js", "browser-turn.js",
]) load(file);

const queuedDice = (values, fallback = 10) => {
  const queue = [...values];
  const roll = (sides) => ((queue.length ? queue.shift() : fallback) - 1) % sides + 1;
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
};
const S = window.IRON_PIT_BROWSER_STATE;
const T = window.IRON_PIT_BROWSER_TURN;
const heroes = window.IRON_PIT_BROWSER_HEROES;
const monsters = window.IRON_PIT_BROWSER_MONSTERS;
const member = (id, side, template, position) => ({
  combatant_id: id, side, position_ft: position, state: S.buildState(structuredClone(template)),
});

assert.equal(Object.keys(monsters).length, 63, "mixed Multiattack batch must bring browser roster to 63 monsters");

{
  const snake = monsters["srd-giant-constrictor-snake"];
  assert.equal(snake.size, "huge");
  assert.equal(snake.armor_class, 12);
  assert.equal(snake.max_hp, 60);
  assert.equal(snake.speed_ft, 30);
  assert.equal(snake.initiative_bonus, 2);
  assert.equal(snake.attacks[0].bonus, 6);
  assert.equal(snake.attacks[0].reach, 10);
  assert.equal(snake.attacks[0].diceCount, 2);
  assert.equal(snake.attacks[0].diceSize, 6);
  assert.equal(snake.attacks[0].damageBonus, 4);
  assert.equal(snake.saving_throw_actions[0].dc, 14);
  assert.equal(snake.saving_throw_actions[0].range, 10);
  assert.equal(snake.saving_throw_actions[0].targetMaxSize, "large");
  assert.equal(snake.saving_throw_actions[0].grappleEscapeDc, 14);
  assert.deepEqual(snake.attack_action.slots, [
    { attackIds: ["giant-constrictor-snake-bite"], saveActionIds: [] },
    { attackIds: [], saveActionIds: ["giant-constrictor-snake-constrict"] },
  ]);
}

{
  const hero = member("hero-1:karnok", "heroes", heroes["karnok-stoneward-l1"], 0);
  const snake = member("monster-1:giant-snake", "monsters", monsters["srd-giant-constrictor-snake"], 10);
  const setup = { heroes: [hero], monsters: [snake] };
  window.IRON_PIT_DICE = queuedDice([15, 1, 1, 1, 1, 1]);

  const result = T.resolveTurn(1, 1, snake, setup);
  const combat = result.events.filter((event) => event.event_type === "attack" || event.event_type === "saving_throw");

  assert.deepEqual(combat.map((event) => event.event_type), ["attack", "saving_throw"]);
  assert.equal(combat[0].weapon_id, "giant-constrictor-snake-bite");
  assert.equal(combat[1].feature_id, "giant-constrictor-snake-constrict");
  assert.equal(combat[1].save_ability, "strength");
  assert.equal(combat[1].save_dc, 14);
  assert.equal(combat[1].save_succeeded, false);
  assert.equal(combat[1].damage_roll.total, 6);
  assert.deepEqual(combat[1].applied_condition_ids, ["grappled"]);
  assert.equal(hero.state.active_effect_ids.includes("restrained"), false);
  assert.equal(snake.state.action_available, false);
}

console.log("Browser mixed weapon/save Multiattack regressions passed.");
