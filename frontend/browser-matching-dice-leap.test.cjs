"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

window.IRON_PIT_BROWSER_STATE = {
  distance: (a, b) => Math.abs((a.state.position?.x || 0) - (b.state.position?.x || 0)) * 5,
};

const resolved = [];
window.IRON_PIT_BROWSER_SPELL_ATTACK = {
  resolve(sequence, round, caster, target, spell) {
    const rolls = (window.IRON_PIT_DICE.rolls || []).splice(0, spell.damageDiceCount);
    const event = {
      sequence,
      round_number: round,
      event_type: "attack",
      actor_id: caster.combatant_id,
      target_id: target.combatant_id,
      hit: true,
      damage_components: [{ source: spell.name, rolls }],
    };
    resolved.push(target.combatant_id);
    target.state.current_hp -= rolls.reduce((sum, value) => sum + value, 0);
    return event;
  },
};

load("browser-matching-dice-leap.js");

function member(id, side, x, hp = 40) {
  return {
    combatant_id: id,
    side,
    state: {
      template: { name: id },
      current_hp: hp,
      is_alive: true,
      is_dead: false,
      position: { x, y: 0 },
    },
  };
}

function setup(caster, ...enemies) {
  return { heroes: [caster], monsters: enemies };
}

const spell = {
  id: "chromatic-orb",
  name: "Chromatic Orb",
  level: 1,
  matchingDiceLeapRangeFt: 30,
  damageDiceCount: 3,
};

const firstEvent = {
  hit: true,
  target_id: "first",
  damage_components: [{ source: "Chromatic Orb", rolls: [4, 4, 1] }],
};

function testLeap(slotLevel, dice, enemies) {
  resolved.length = 0;
  window.IRON_PIT_DICE = { rolls: dice };
  const caster = member("caster", "heroes", 0);
  const first = member("first", "monsters", 6);
  const setupEnemies = [first, ...enemies];
  return window.IRON_PIT_BROWSER_MATCHING_DICE_LEAP.resolve(
    2, 1, caster, first, firstEvent, spell, setup(caster, ...setupEnemies), "1:caster",
    { slotLevel },
  );
}

const oneLeap = testLeap(1, [5, 5, 2, 1, 2, 3], [
  member("second", "monsters", 12),
  member("third", "monsters", 18),
]);
assert.deepEqual(resolved, ["second"]);
assert.equal(oneLeap.events.length, 1);

resolved.length = 0;
const unmatched = window.IRON_PIT_BROWSER_MATCHING_DICE_LEAP.resolve(
  2, 1, member("caster", "heroes", 0), member("first", "monsters", 6),
  { hit: true, target_id: "first", damage_components: [{ source: "Chromatic Orb", rolls: [1, 2, 3] }] },
  spell, setup(member("caster", "heroes", 0), member("first", "monsters", 6), member("second", "monsters", 12)),
  "1:caster", { slotLevel: 1 },
);
assert.deepEqual(resolved, []);
assert.equal(unmatched.events.length, 0);

const twoLeaps = testLeap(2, [5, 5, 2, 1, 2, 3], [
  member("second", "monsters", 12),
  member("third", "monsters", 18),
]);
assert.deepEqual(resolved, ["second", "third"]);
assert.equal(twoLeaps.events.length, 2);

resolved.length = 0;
const beyond = window.IRON_PIT_BROWSER_MATCHING_DICE_LEAP.resolve(
  2, 1, member("caster", "heroes", 0), member("first", "monsters", 18),
  firstEvent, spell,
  setup(member("caster", "heroes", 0), member("first", "monsters", 18), member("second", "monsters", 24)),
  "1:caster", { slotLevel: 1 },
);
assert.deepEqual(resolved, ["second"]);

assert.equal(
  window.IRON_PIT_BROWSER_MATCHING_DICE_LEAP.matchingFaces(firstEvent, spell),
  true,
);
assert.equal(
  window.IRON_PIT_BROWSER_MATCHING_DICE_LEAP.matchingFaces(
    { hit: false, damage_components: [{ source: "Chromatic Orb", rolls: [4, 4, 1] }] },
    spell,
  ),
  false,
);
