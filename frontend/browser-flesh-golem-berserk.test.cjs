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

let rolls = [6, 1];
window.IRON_PIT_DICE = { roll: () => rolls.shift() };
window.IRON_PIT_BROWSER_STATE = {
  effectiveMaxHp: (state) => state.template.max_hp,
  distance: (left, right) => Math.abs(left.position_ft - right.position_ft),
};
load("browser-bloodied-berserk.js");

const flesh = {
  combatant_id: "flesh",
  side: "monsters",
  position_ft: 0,
  state: {
    current_hp: 63,
    is_alive: true,
    is_dead: false,
    active_berserk_rule_id: null,
    swallowed: null,
    template: {
      id: "srd-flesh-golem",
      name: "Flesh Golem",
      max_hp: 127,
      bloodied_berserk_rule: {
        id: "berserk",
        name: "Berserk",
        dieSize: 6,
        triggerMinimum: 6,
        targetMode: "nearest_living_creature",
        remainsWhileBloodied: true,
        creatorCalmingOutsideArena: true,
      },
    },
  },
};
const ally = {
  combatant_id: "ally", side: "monsters", position_ft: 5,
  state: { current_hp: 10, is_alive: true, is_dead: false, swallowed: null, template: { name: "Ally" } },
};
const hero = {
  combatant_id: "hero", side: "heroes", position_ft: 20,
  state: { current_hp: 10, is_alive: true, is_dead: false, swallowed: null, template: { name: "Hero" } },
};
const setup = { heroes: [hero], monsters: [flesh, ally] };

const first = window.IRON_PIT_BROWSER_BLOODIED_BERSERK.startTurn(1, 1, flesh);
assert.equal(first.sequence, 2);
assert.equal(first.event.resource_roll.total, 6);
assert.equal(flesh.state.active_berserk_rule_id, "berserk");
assert.equal(window.IRON_PIT_BROWSER_BLOODIED_BERSERK.targetOrder(flesh, setup)[0].combatant_id, "ally");

const second = window.IRON_PIT_BROWSER_BLOODIED_BERSERK.startTurn(2, 2, flesh);
assert.equal(second.sequence, 3);
assert.equal(second.event.resource_roll.total, 1);
assert.equal(flesh.state.active_berserk_rule_id, "berserk");

flesh.state.current_hp = 127;
const cleared = window.IRON_PIT_BROWSER_BLOODIED_BERSERK.startTurn(3, 3, flesh);
assert.equal(cleared.event, null);
assert.equal(cleared.sequence, 3);
assert.equal(flesh.state.active_berserk_rule_id, null);

console.log("Browser Flesh Golem Berserk parity passed.");
