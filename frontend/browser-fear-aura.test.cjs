"use strict";

const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

const S = window.IRON_PIT_BROWSER_STATE;
const E = window.IRON_PIT_BROWSER_TIMED_EMANATIONS;
const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];
let queue = [];

function setDice(values) {
  try {
    queue = [...values];
    window.IRON_PIT_DICE = {
      roll(sides) {
        assert.equal(sides, 20);
        assert.ok(queue.length, "Unexpected Fear Aura save roll.");
        return queue.shift();
      },
      rollMany(count, sides) {
        return Array.from({ length: count }, () => this.roll(sides));
      },
    };
  } catch (error) {
    console.error("Failed to configure Fear Aura browser dice", { error });
    throw error;
  }
}

function member(id, side, position, source = false) {
  try {
    const template = structuredClone(base);
    Object.assign(template, {
      id: "template-" + id,
      name: id,
      kind: source ? "monster" : "character",
      ruleset: "2014",
      creature_type: source ? "fiend" : "humanoid",
      saving_throw_bonuses: {
        ...template.saving_throw_bonuses,
        wisdom: 5,
      },
      timed_self_buff_actions: source ? [{
        id: "renamed-dread-aura",
        name: "Renamed Dread Aura",
        actionCost: "action",
        activationTiming: "passive",
        durationRounds: null,
        expiryTiming: null,
        hostileStartTurnConditionAura: {
          trigger: "enemy_turn_start",
          radius_ft: 20,
          save_ability: "wisdom",
          save_dc: 21,
          condition_id: "frightened",
          success_immunity: true,
          source_is_magical: false,
          requires_source_not_incapacitated: true,
          condition_duration_rounds: null,
          condition_expiry_timing: "target_turn_start",
          effect_tags: ["fear"],
        },
      }] : [],
    });
    return {
      combatant_id: id,
      side,
      position_ft: position,
      state: S.buildState(template),
    };
  } catch (error) {
    console.error("Failed to build Fear Aura browser combatant", { id, error });
    throw error;
  }
}

function fixture() {
  try {
    const source = member("renamed-source", "monsters", 0, true);
    const target = member("renamed-target", "heroes", 20, false);
    return { source, target, setup: { heroes: [target], monsters: [source] } };
  } catch (error) {
    console.error("Failed to build Fear Aura browser fixture", { error });
    throw error;
  }
}

try {
  const { source, target, setup } = fixture();
  source.state.active_effect_ids.push("incapacitated");
  setDice([]);
  assert.deepEqual(
    E.resolveStartOfTurn(1, 1, target, setup),
    { events: [], sequence: 1 },
  );
  assert.deepEqual(queue, []);

  source.state.active_effect_ids = source.state.active_effect_ids
    .filter((id) => id !== "incapacitated");
  setDice([1]);
  const failed = E.resolveStartOfTurn(1, 2, target, setup);
  assert.equal(failed.events.length, 1);
  assert.deepEqual(failed.events[0].applied_condition_ids, ["frightened"]);
  const fear = target.state.timed_effects.find((item) => item.effect_id === "frightened");
  assert.ok(fear);
  assert.equal(fear.expiry_timing, "target_turn_start");
} catch (error) {
  console.error("Fear Aura source-incapacitation browser regression failed", { error });
  throw error;
}

try {
  const { source, target, setup } = fixture();
  setDice([20]);
  const passed = E.resolveStartOfTurn(1, 1, target, setup);
  assert.equal(passed.events[0].save_succeeded, true);
  assert.match(passed.events[0].description, /rest of the match/);
  setDice([]);
  const repeated = E.resolveStartOfTurn(passed.sequence, 500, target, setup);
  assert.deepEqual(repeated.events, []);
  assert.deepEqual(queue, []);
  assert.equal(source.state.template.timed_self_buff_actions[0].id, "renamed-dread-aura");
} catch (error) {
  console.error("Fear Aura source-immunity browser regression failed", { error });
  throw error;
}

console.log("Universal passive Fear Aura browser regressions passed.");
