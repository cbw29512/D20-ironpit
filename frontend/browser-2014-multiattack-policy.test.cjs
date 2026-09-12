"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

window.IRON_PIT_ACTION_ECONOMY = {
  available: (state) => state.action_available,
  spend: (state) => { state.action_available = false; },
};
window.IRON_PIT_BROWSER_CHARGE = { openingFeature: () => null };
window.IRON_PIT_BROWSER_AREA_SAVES = { choice: () => null };
window.IRON_PIT_BROWSER_SAVES = { legalAction: () => false };
window.IRON_PIT_BROWSER_LIGHT_ATTACK = { resolve: (sequence) => ({ events: [], sequence }) };
window.IRON_PIT_BROWSER_WEAPON_MASTERY = { resolveCleave: (sequence) => ({ events: [], sequence }) };
window.IRON_PIT_BROWSER_STATE = { packTactics: () => false };

function setupRuntime(rolls, hits) {
  const dice = [...rolls], hitQueue = [...hits];
  window.IRON_PIT_DICE = { roll: () => dice.shift() };
  window.IRON_PIT_BROWSER_ATTACK = {
    resolveAttack: (sequence, _round, _member, target, attack) => ({
      sequence, target_id: target.combatant_id, attack_name: attack.name,
      hit: hitQueue.length ? hitQueue.shift() : true,
    }),
  };
}

function member(definition, attacks) {
  return {
    combatant_id: "monster", side: "monsters",
    state: {
      action_available: true, is_dead: false, is_unconscious: false, turn_terminated: false,
      template: { name: "monster", attack_action: definition, attacks, saving_throw_actions: [] },
    },
  };
}

const targetA = { combatant_id: "hero-a", side: "heroes", state: { is_alive: true, is_dead: false, current_hp: 20, template: { name: "A" } } };
const targetB = { combatant_id: "hero-b", side: "heroes", state: { is_alive: true, is_dead: false, current_hp: 20, template: { name: "B" } } };
const setup = { heroes: [targetA, targetB], monsters: [] };

window.IRON_PIT_BROWSER_FORMATION = {
  targetOrder: () => [targetA, targetB], isBackline: () => false,
  alliedFrontlineActive: () => false, hasFrontlineTarget: () => true, hasBacklineTarget: () => false,
  flexibleSlotHasBoth: () => false,
  chooseAttack: (actor, _setup, ids, kind, _prefer, requiredTargetId) => {
    const attack = actor.state.template.attacks.find((item) => ids.includes(item.id) && (!kind || item.kind === kind));
    const target = requiredTargetId ? [targetA, targetB].find((item) => item.combatant_id === requiredTargetId) : targetA;
    return attack && target ? { target, attack, distance: 5 } : null;
  },
};

load("browser-multiattack.js");

const tentacles = { id: "tentacles", name: "Tentacles", kind: "melee" };
const beak = { id: "beak", name: "Beak", kind: "melee" };
setupRuntime([], [true, true]);
let actor = member({
  id: "grick", slots: [{ attackIds: ["tentacles"] }, { attackIds: ["beak"] }],
  policy: { requiresPreviousHitSlots: [1], sameTargetAsPreviousSlots: [1] },
}, [tentacles, beak]);
setup.monsters = [actor];
let result = window.IRON_PIT_BROWSER_MULTIATTACK.resolveAttackAction(1, 1, actor, setup);
assert.deepEqual(result.events.map((event) => event.attack_name), ["Tentacles", "Beak"]);
assert.equal(result.events[1].target_id, result.events[0].target_id);

setupRuntime([], [false]);
actor = member({
  id: "grick", slots: [{ attackIds: ["tentacles"] }, { attackIds: ["beak"] }],
  policy: { requiresPreviousHitSlots: [1], sameTargetAsPreviousSlots: [1] },
}, [tentacles, beak]);
setup.monsters = [actor];
result = window.IRON_PIT_BROWSER_MULTIATTACK.resolveAttackAction(1, 1, actor, setup);
assert.equal(result.events.length, 1);

const bite = { id: "bite", name: "Bite", kind: "melee" };
const club = { id: "club", name: "Club", kind: "melee" };
setupRuntime([], [true, true]);
actor = member({
  id: "lizardfolk", slots: [{ attackIds: ["bite", "club"] }, { attackIds: ["bite", "club"] }],
  policy: { distinctAttackIds: true },
}, [bite, club]);
setup.monsters = [actor];
result = window.IRON_PIT_BROWSER_MULTIATTACK.resolveAttackAction(1, 1, actor, setup);
assert.deepEqual(result.events.map((event) => event.attack_name), ["Bite", "Club"]);

const touch = { id: "rotting-touch", name: "Rotting Touch", kind: "melee" };
setupRuntime([4], [true, true, true, true]);
actor = member({
  id: "fungus", slots: [{ attackIds: ["rotting-touch"] }],
  policy: { repeatSlotIndex: 0, repeatDiceCount: 1, repeatDiceSize: 4 },
}, [touch]);
setup.monsters = [actor];
result = window.IRON_PIT_BROWSER_MULTIATTACK.resolveAttackAction(1, 1, actor, setup);
assert.equal(result.events.length, 4);

console.log("2014 browser Multiattack policy regressions passed.");
