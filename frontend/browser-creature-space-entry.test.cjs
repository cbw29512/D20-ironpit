"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
load("browser-on-hit-recurring-damage.js");
load("browser-creature-space-entry.js");

const diceQueue = [7, 4, 6, 8, 4, 5];
window.IRON_PIT_DICE = {
  rollMany: (count) => Array.from({ length: count }, () => diceQueue.shift() ?? 3),
};
window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES = {
  resolveDamage: (state, total, damageType) => ({
    applied: state.template.damage_immunities?.includes(damageType) ? 0 : total,
  }),
};
window.IRON_PIT_BROWSER_ATTACK = {
  applyDamage: (state, amount) => {
    state.current_hp = Math.max(0, state.current_hp - amount);
    if (!state.current_hp) { state.is_dead = true; state.is_alive = false; }
  },
};

const rule = {
  diceCount: 1, diceSize: 10, damageType: "fire",
  recurringDamage: {
    effectId: "burning", diceCount: 1, diceSize: 10, damageType: "fire",
    tickTiming: "target_turn_start", stacking: "nonstacking",
    endsIfSourceDead: false, removalActionIds: ["douse-fire"],
  },
};
function member(id, side, position, action = null, immunity = false) {
  return {
    combatant_id: id, side,
    state: {
      template: {
        name: id, damage_immunities: immunity ? ["fire"] : [],
        timed_self_buff_actions: action ? [{
          id: "test-entry", name: "Blazing Body", activationTiming: "passive",
          creatureSpaceEntryDamage: rule,
        }] : [],
      },
      position, current_hp: 100, is_dead: false, is_alive: true,
      timed_effects: [], active_effect_ids: [], feature_last_turn_keys: {},
    },
  };
}
const source = member("source", "monsters", { x: 1, y: 1 }, true);
const enemy = member("enemy", "heroes", { x: 1, y: 1 });
const ally = member("ally", "monsters", { x: 1, y: 1 });
const immune = member("immune", "heroes", { x: 1, y: 1 }, false, true);
const setup = { heroes: [enemy, immune], monsters: [source, ally] };
const runtime = window.IRON_PIT_BROWSER_CREATURE_SPACE_ENTRY;

const first = runtime.resolve(1, 1, source, setup, "1:source");
assert.equal(first.events.length, 3);
assert.equal(first.sequence, 4);
assert.equal(enemy.state.current_hp, 93);
assert.equal(ally.state.current_hp, 94);
assert.equal(immune.state.current_hp, 100);
for (const target of [enemy, ally, immune]) {
  assert.equal(target.state.timed_effects.length, 1);
  assert.equal(target.state.timed_effects[0].effect_id, "burning");
  assert.equal(target.state.timed_effects[0].source_name, "Blazing Body");
}
const repeated = runtime.resolve(4, 1, source, setup, "1:source");
assert.equal(repeated.events.length, 0);
assert.equal(enemy.state.current_hp, 93);

const second = runtime.resolve(4, 2, source, setup, "2:source");
assert.equal(second.events.length, 3);
assert.equal(enemy.state.current_hp, 85);
assert.equal(ally.state.current_hp, 89);
assert.equal(enemy.state.timed_effects.length, 1, "Entry never stacks Burning.");

enemy.state.position = { x: 2, y: 2 };
const none = runtime.resolve(7, 2, source, setup, "3:source");
assert.equal(none.events.length, 2, "Only actually occupied squares trigger.");
assert.ok(first.events.every((event) => event.feature_id === "Blazing Body"));
// Verify that the real source card, not only a synthetic fixture, is exposed
// with the generic movement trigger and accurate permanent status lanes.
load("browser-monsters-2014.js");
load("battlefield-passive-states.js");
const fire = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-fire-elemental"];
assert.ok(fire, "The admitted 2014 Fire Elemental must be in the browser roster.");
assert.equal(fire.source_allows_hostile_overlap, true);
assert.equal(fire.timed_self_buff_actions.find((a) => a.name === "Fire Form")
  .creatureSpaceEntryDamage.recurringDamage.effectId, "burning");
const passives = window.IRON_PIT_BATTLEFIELD_PASSIVE_STATES.permanentPassiveStates({
  combatant_id: "source-card-fire-elemental",
  state: {
    template: fire,
    active_modifiers: [],
    active_effect_ids: [],
  },
}, {});
const fireForm = passives.find((p) => (p.label || p.id) === "Fire Form");
const water = passives.find((p) => (p.label || p.id) === "Water Susceptibility");
assert.ok(fireForm && fireForm.active, "Fire Form is an always-active permanent buff.");
assert.ok(water && !water.active, "Water Susceptibility stays grey in the dry arena.");
assert.equal(water.lane, "buff", "Printed source traits remain visible in the buff lane.");

console.log("Universal creature-space entry and recurring Burning parity passed.");
