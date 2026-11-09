"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
function load(file) {
  vm.runInThisContext(fs.readFileSync(path.join(__dirname, file), "utf8"), { filename: file });
}

load("browser-breathing.js");
load("browser-grapple.js");
const breath = window.IRON_PIT_BROWSER_BREATHING;
let zeroCalls = 0;
window.IRON_PIT_BROWSER_ZERO_HP = {
  // Stub only the existing universal zero-HP transition; countdown must drive it.
  reduceToZero(state) {
    zeroCalls++;
    state.current_hp = 0;
    state.is_unconscious = true;
    state.is_stable = false;
    return "unconscious";
  },
};
function build({ con = 14, needsAir = true, hold = null, ruleset = "2014" } = {}) {
  const owner = {
    combatant_id: "owner", state: { template: {
      saving_throw_actions: [{ id: "undertow", name: "Undertow" }],
    } },
  };
  const member = {
    combatant_id: "victim",
    state: {
      template: {
        name: "Synthetic Swimmer", ruleset, needs_air: needsAir,
        ability_scores: { constitution: con }, breath_hold_rounds: hold,
      },
      current_hp: 15, is_dead: false, is_alive: true, is_unconscious: false,
      is_stable: false, active_effect_ids: [], timed_effects: [],
      grapple_sources: [{
        source_id: "owner", escape_dc: 14, range_ft: 5, restrains: true,
        prevents_breathing: true, linked_effect_id: "undertow",
      }],
      breath_hold_rounds_remaining: null,
      breath_survival_rounds_remaining: null, suffocating_at_zero: false,
    },
  };
  const setup = { heroes: [member], monsters: [owner] };
  return { member, owner, setup };
}
function tick(member, setup, round) {
  return breath.startTurn(round, round, member, setup);
}

{
  const { member, setup } = build();
  for (let round = 1; round <= 29; round++) {
    assert.deepEqual(tick(member, setup, round).events, []);
  }
  assert.equal(member.state.breath_hold_rounds_remaining, 1);
  const warned = tick(member, setup, 30).events;
  assert.equal(warned.length, 1);
  assert.match(warned[0].description, /Undertow/);
  assert.equal(tick(member, setup, 31).events.length, 0);
  assert.equal(tick(member, setup, 32).events.length, 0);
  const down = tick(member, setup, 33).events;
  assert.equal(down.length, 1);
  assert.match(down[0].description, /Undertow/);
  assert.equal(zeroCalls, 1);
  assert.equal(member.state.current_hp, 0);
  assert.equal(breath.blocksRecovery(member.state), true);
  assert.equal(tick(member, setup, 34).events.length, 0);
  window.IRON_PIT_BROWSER_GRAPPLE.release(member.state, "owner");
  assert.equal(breath.blocksRecovery(member.state), false);
  assert.equal(member.state.breath_hold_rounds_remaining, null);
  assert.equal(member.state.suffocating_at_zero, false);
}

{
  const { member, setup } = build({ hold: 2 });
  assert.equal(tick(member, setup, 1).events.length, 0);
  assert.equal(tick(member, setup, 2).events.length, 1);
  assert.equal(tick(member, setup, 3).events.length, 0);
  assert.equal(tick(member, setup, 4).events.length, 0);
  assert.equal(tick(member, setup, 5).events.length, 1);
  assert.equal(member.state.current_hp, 0);
}
{
  const { member, setup } = build({ needsAir: false });
  for (let round = 1; round <= 50; round++) {
    assert.equal(tick(member, setup, round).events.length, 0);
  }
  assert.equal(member.state.current_hp, 15);
}
{
  const { member, setup } = build({ ruleset: "2024" });
  assert.throws(() => tick(member, setup, 1), /2024 suffocation/);
}

console.log("2014 universal browser suffocation, release, no-air and edition isolation passed.");
