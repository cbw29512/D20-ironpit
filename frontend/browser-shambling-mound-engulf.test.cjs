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

window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_CONDITION_RULES = { has: () => false, speedZero: () => false };
window.IRON_PIT_BROWSER_STATE = {
  sizeAtMost: (target, maximum) => {
    const order = ["tiny", "small", "medium", "large", "huge", "gargantuan"];
    return order.indexOf(target.state.template.size) <= order.indexOf(maximum);
  },
};
window.IRON_PIT_BROWSER_ONGOING_DAMAGE = {
  resolve: (sequence, round, source, target, _setup, spec) => {
    const total = 9;
    target.state.current_hp -= total;
    return {
      sequence,
      round_number: round,
      actor_id: source.combatant_id,
      target_id: target.combatant_id,
      feature_id: spec.featureId,
      damage_roll: { total },
    };
  },
};

load("browser-save-legality.js");
load("browser-grapple.js");

const engulf = {
  id: "srd-shambling-mound-engulf",
  name: "Engulf",
  range: 5,
  targetMaxSize: "medium",
  maxActiveGrappleTargets: 1,
  grapplePeriodicDamage: {
    timing: "target_turn_start",
    diceCount: 3,
    diceSize: 6,
    damageBonus: 0,
    damageType: "lightning",
  },
};

const mound = {
  combatant_id: "mound",
  side: "monsters",
  state: {
    is_alive: true,
    is_dead: false,
    template: { name: "Shambling Mound", saving_throw_actions: [engulf] },
  },
};
const first = {
  combatant_id: "first",
  side: "heroes",
  state: {
    current_hp: 20,
    is_alive: true,
    is_dead: false,
    active_effect_ids: [],
    timed_effects: [],
    grapple_sources: [],
    template: { name: "First", size: "medium" },
  },
};
const second = {
  combatant_id: "second",
  side: "heroes",
  state: {
    current_hp: 20,
    is_alive: true,
    is_dead: false,
    active_effect_ids: [],
    timed_effects: [],
    grapple_sources: [],
    template: { name: "Second", size: "medium" },
  },
};
const setup = { heroes: [first, second], monsters: [mound] };
const G = window.IRON_PIT_BROWSER_GRAPPLE;
const L = window.IRON_PIT_BROWSER_SAVE_LEGALITY;

const applied = G.apply(
  first.state, mound.combatant_id, 14, 5, true, ["blinded"], engulf.id,
);
assert.deepEqual(new Set(applied), new Set(["grappled", "restrained", "blinded"]));
assert.equal(L.legalAction(engulf, second, 5, mound, setup), false);

const periodic = G.periodicTurnStart(1, 2, first, setup);
assert.equal(periodic.sequence, 2);
assert.equal(periodic.events.length, 1);
assert.equal(periodic.events[0].feature_id, engulf.id);
assert.equal(first.state.current_hp, 11);

G.release(first.state, mound.combatant_id);
assert.equal(first.state.active_effect_ids.includes("blinded"), false);
assert.equal(first.state.active_effect_ids.includes("restrained"), false);
assert.equal(L.legalAction(engulf, second, 5, mound, setup), true);
assert.equal(G.periodicTurnStart(2, 3, first, setup).events.length, 0);

console.log("Browser Shambling Mound Engulf grapple lifecycle parity passed.");
