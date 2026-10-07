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

load("browser-damage-triggered-d20-debuff.js");
load("browser-exhaustion.js");

window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS = { endDamageSensitive: () => {} };
window.IRON_PIT_BROWSER_STATE = {
  effectiveMaxHp: (state) => state.template.max_hp + (state.max_hp_bonus || 0),
};
load("browser-zero-hp.js");

function state() {
  return {
    template: {
      name: "Yeti",
      kind: "monster",
      ruleset: "2014",
      max_hp: 51,
      traits: [],
      damage_triggered_d20_debuffs: [{
        sourceId: "fear-of-fire",
        sourceName: "Fear of Fire",
        triggerDamageType: "fire",
        triggerDamageMinimum: 1,
        attackRollDisadvantage: true,
        abilityCheckDisadvantage: true,
        durationTargetTurns: 1,
      }],
    },
    current_hp: 51,
    max_hp_bonus: 0,
    temporary_hp: 0,
    is_alive: true,
    is_dead: false,
    is_unconscious: false,
    is_stable: false,
    concentration: null,
    replacement_form: null,
    active_effect_ids: [],
    damage_types_taken_since_regen: [],
    damage_taken_this_turn_by_type: {},
    active_damage_triggered_d20_debuffs: [],
    turns_started_count: 0,
    damage_share_source_id: null,
    exhaustion_level: 0,
  };
}

const component = (type, amount) => ({
  damage_type: type,
  applied_total: amount,
});

{
  const yeti = state();
  window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(
    yeti, 5, false, ["fire"], [], null, [component("fire", 5)],
  );
  assert.equal(yeti.current_hp, 46);
  assert.equal(yeti.active_damage_triggered_d20_debuffs.length, 1);
  assert.equal(yeti.active_damage_triggered_d20_debuffs[0].sourceName, "Fear of Fire");
  assert.equal(window.IRON_PIT_BROWSER_EXHAUSTION.attackDisadvantage(yeti), 1);
  assert.equal(window.IRON_PIT_BROWSER_EXHAUSTION.abilityCheckDisadvantage(yeti), 1);
  assert.equal(window.IRON_PIT_BROWSER_EXHAUSTION.saveDisadvantage(yeti), 0);

  yeti.turns_started_count = 1;
  assert.deepEqual(
    window.IRON_PIT_BROWSER_DAMAGE_TRIGGERED_D20_DEBUFF.expireTargetTurn(yeti),
    ["Fear of Fire"],
  );
  assert.equal(yeti.active_damage_triggered_d20_debuffs.length, 0);
}

{
  const yeti = state();
  yeti.turns_started_count = 1;
  window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(
    yeti, 5, false, ["fire"], [], null, [component("fire", 5)],
  );
  assert.equal(yeti.active_damage_triggered_d20_debuffs[0].expiresAfterTargetTurnCount, 2);

  assert.deepEqual(
    window.IRON_PIT_BROWSER_DAMAGE_TRIGGERED_D20_DEBUFF.expireTargetTurn(yeti),
    [],
  );
  assert.equal(window.IRON_PIT_BROWSER_EXHAUSTION.attackDisadvantage(yeti), 1);

  yeti.turns_started_count = 2;
  assert.deepEqual(
    window.IRON_PIT_BROWSER_DAMAGE_TRIGGERED_D20_DEBUFF.expireTargetTurn(yeti),
    ["Fear of Fire"],
  );
  assert.equal(window.IRON_PIT_BROWSER_EXHAUSTION.attackDisadvantage(yeti), 0);
}

{
  const yeti = state();
  window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(
    yeti, 5, false, ["cold"], [], null, [component("cold", 5)],
  );
  assert.equal(yeti.active_damage_triggered_d20_debuffs.length, 0);
}

console.log("Browser damage-triggered D20 debuff regressions passed.");
