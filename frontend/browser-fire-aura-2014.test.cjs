"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
load("browser-damage-defense-rules.js");
load("browser-melee-retaliation.js");
load("browser-emanation-save-damage.js");
load("browser-timed-emanations.js");

const aura = {
  id: "fire-aura", name: "Fire Aura", activationTiming: "passive",
  meleeHitRetaliation: { rangeFt: 5, diceCount: 3, diceSize: 6, damageType: "fire", onContact: true },
  startTurnEmanationDamage: {
    trigger: "source_turn_start", radius_ft: 5, dice_count: 3, dice_size: 6, damage_type: "fire",
  },
};
const member = (id, side, pos, actions = []) => ({
  combatant_id: id, side, position_ft: pos,
  state: {
    template: { name: id, timed_self_buff_actions: actions, damage_resistances: [], damage_immunities: [], damage_vulnerabilities: [], damage_absorptions: [] },
    current_hp: 100, is_alive: true, is_dead: false, timed_effects: [], temporary_damage_resistances: [],
    emanation_triggers_this_turn: {},
  },
});
const balor = member("balor", "monsters", 0, [aura]);
const hero = member("hero", "heroes", 5);
window.IRON_PIT_DICE = { rollMany: () => [6, 6, 6] };
window.IRON_PIT_BROWSER_STATE = { distance: (a, b) => Math.abs(a.position_ft - b.position_ft) };
window.IRON_PIT_BROWSER_ATTACK = {
  applyDamage: (state, amount) => { state.current_hp -= amount; },
};
const applied = window.IRON_PIT_BROWSER_MELEE_RETALIATION.apply(hero, balor, { melee: true });
assert.equal(applied, 18);
assert.equal(hero.state.current_hp, 82);
hero.position_ft = 10;
assert.equal(window.IRON_PIT_BROWSER_MELEE_RETALIATION.apply(hero, balor, { melee: true }), 0);
hero.position_ft = 5;
const setup = { heroes: [hero], monsters: [balor] };
const result = window.IRON_PIT_BROWSER_TIMED_EMANATIONS.resolveSourceTurnStart(1, 1, balor, setup);
assert.equal(result.events.length, 1);
assert.equal(hero.state.current_hp, 64);
console.log("2014 Fire Aura browser parity passed.");
