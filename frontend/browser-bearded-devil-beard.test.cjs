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

window.IRON_PIT_BROWSER_STATE = {
  effectiveMaxHp: (state) => state.template.max_hp,
};
window.IRON_PIT_DICE = { roll: () => 1 };
load("browser-modifiers.js");
load("browser-timed-conditions.js");
load("browser-healing.js");

const source = {
  combatant_id: "devil",
  side: "monsters",
  state: {
    active_modifiers: [], timed_effects: [], active_effect_ids: [],
    template: { name: "Bearded Devil", max_hp: 52, traits: [] },
  },
};
const target = {
  combatant_id: "target",
  side: "heroes",
  state: {
    current_hp: 5, active_modifiers: [], timed_effects: [], active_effect_ids: [],
    is_alive: true, is_dead: false, is_unconscious: false, is_stable: false,
    death_save_successes: 0, death_save_failures: 0,
    template: { name: "Target", max_hp: 20, traits: [] },
  },
};
const setup = { heroes: [target], monsters: [source] };

window.IRON_PIT_BROWSER_TIMED.apply(
  target.state,
  "poisoned",
  source.combatant_id,
  {
    sourceEffectId: "srd-bearded-devil-beard",
    appliedRound: 1,
    expiryTiming: "source_turn_start",
  },
);
window.IRON_PIT_BROWSER_MODIFIERS.applyEffect(
  target.state,
  source.combatant_id,
  "srd-bearded-devil-beard",
  {
    kind: "healing-prevented",
    flatBonus: 0,
    expiresAtStartOfSourceTurn: true,
  },
  0,
  "hit",
  1,
);

assert.equal(window.IRON_PIT_BROWSER_HEALING.restore(target.state, 5), 0);
assert.equal(target.state.current_hp, 5);
assert.ok(target.state.active_effect_ids.includes("poisoned"));
assert.equal(target.state.active_modifiers[0].kind, "healing-prevented");

assert.equal(
  window.IRON_PIT_BROWSER_MODIFIERS.expireSourceTurnStart(
    [source.state, target.state],
    source.combatant_id,
  ),
  1,
);
const expired = window.IRON_PIT_BROWSER_TIMED.expireSourceStart(
  1, 2, source, setup,
);
assert.equal(expired.events.length, 1);
assert.ok(!target.state.active_effect_ids.includes("poisoned"));
assert.equal(target.state.active_modifiers.length, 0);
assert.equal(window.IRON_PIT_BROWSER_HEALING.restore(target.state, 5), 5);
assert.equal(target.state.current_hp, 10);

console.log("Browser Bearded Devil Beard healing-prevention lifecycle passed.");
