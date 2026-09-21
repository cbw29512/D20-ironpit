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

window.IRON_PIT_BROWSER_STATE = { distance: () => 5 };
load("browser-offense-priority.js");
load("browser-formation.js");

const dagger = {
  id: "dagger", name: "Dagger", kind: "melee",
  diceCount: 1, diceSize: 4, damageBonus: 3, bonus: 5, reach: 5,
};
const greatsword = {
  id: "greatsword", name: "Greatsword", kind: "melee",
  diceCount: 2, diceSize: 6, damageBonus: 3, bonus: 5, reach: 5,
};
const actor = {
  combatant_id: "fighter", side: "heroes",
  state: {
    is_alive: true, is_dead: false, current_hp: 20,
    template: { attacks: [dagger, greatsword], primary_attack_id: "dagger" },
  },
};
const target = {
  combatant_id: "target", side: "monsters",
  state: {
    is_alive: true, is_dead: false, current_hp: 20, grapple_sources: [],
    template: { attacks: [], primary_attack_id: null },
  },
};

const choice = window.IRON_PIT_BROWSER_FORMATION.chooseStandardAttack(
  actor, { heroes: [actor], monsters: [target] },
);
assert.ok(choice);
assert.equal(choice.attack.id, "greatsword");

console.log("Browser weapon policy chooses strongest legal weapon, not first-listed weapon.");
