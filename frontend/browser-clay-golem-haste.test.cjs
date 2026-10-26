"use strict";
const assert = require("node:assert/strict");
const { loadWebsite } = require("./browser-test-runtime.cjs");
loadWebsite();

const S = window.IRON_PIT_BROWSER_STATE;
const B = window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS;
const M = window.IRON_PIT_BROWSER_MODIFIERS;
const V = window.IRON_PIT_BROWSER_SAVING_THROWS;
const BA = window.IRON_PIT_BROWSER_BONUS_ATTACKS;
const R = window.IRON_PIT_BROWSER_RECHARGE;
const L = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE;
const base = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-commoner"];

function makeFight() {
  try {
    const action = {
      id: "haste", name: "Haste", actionCost: "action", activationTiming: "action",
      resourceId: "haste", resourceCost: 1, durationRounds: 1,
      conditionIds: [], damageResistances: [], magicalEffect: true,
      expiryTiming: "source_turn_end", priority: 80, animation: "buff",
      savingThrowAdvantageGrants: [{
        source_id: "haste", source_name: "Haste", abilities: ["dexterity"],
      }],
      modifierEffects: [{ kind: "armor-class", flatBonus: 2 }],
    };
    const slam = {
      ...structuredClone(base.attacks[0]), id: "synthetic-slam", name: "Slam",
      bonus: 8, diceCount: 2, diceSize: 10, damageBonus: 5,
    };
    const template = {
      ...structuredClone(base), id: "synthetic-clay", name: "Synthetic Clay",
      armor_class: 14, max_hp: 133, speed_ft: 20,
      attacks: [slam], primary_attack_id: slam.id,
      resources: { haste: 1 },
      recharge_rules: [{ resourceId: "haste", minimumRoll: 5, dieSize: 6 }],
      timed_self_buff_actions: [action],
      bonusAttackGrants: [{
        id: "haste-bonus-attack", name: "Haste", attackIds: [slam.id],
        attackCount: 1, trigger: "always", resourceId: null, resourceCost: 1,
        requiredActiveEffectId: "haste", priority: 20,
      }],
    };
    const targetTemplate = {
      ...structuredClone(base), id: "target", name: "Target", armor_class: 1, max_hp: 100,
    };
    const golem = {
      combatant_id: "clay", side: "monsters", position_ft: 5,
      state: S.buildState(template),
    };
    const target = {
      combatant_id: "target", side: "heroes", position_ft: 0,
      state: S.buildState(targetTemplate),
    };
    return { action, golem, target, setup: { heroes: [target], monsters: [golem] } };
  } catch (error) {
    console.error("Failed to build synthetic Clay Haste browser fight", { error });
    throw error;
  }
}

function dice(values) {
  try {
    const queue = [...values];
    window.IRON_PIT_DICE = {
      roll: (sides) => ((queue.shift() ?? 10) - 1) % sides + 1,
      rollMany: (count, sides) =>
        Array.from({ length: count }, () => window.IRON_PIT_DICE.roll(sides)),
    };
  } catch (error) {
    console.error("Failed to configure Clay Haste browser dice", { error });
    throw error;
  }
}

{
  const { action, golem, target, setup } = makeFight();
  const blocked = BA.resolve(1, 1, golem, setup, "1:clay");
  assert.deepEqual(blocked.events, []);
  assert.equal(golem.state.bonus_action_available, true);

  const speedBefore = M.effectiveSpeed(golem.state);
  const event = B.resolve(1, 1, golem, action, {
    affectedStates: [golem.state, target.state], setup,
  });
  assert.equal(event.feature_id, "haste");
  assert.equal(event.resource_remaining, 0);
  assert.equal(golem.state.action_available, false);
  assert.equal(golem.state.bonus_action_available, true);
  assert.equal(M.effectiveArmorClass(golem.state), 16);
  assert.equal(V.saveMode(golem.state, "dexterity"), "advantage");
  assert.equal(V.saveMode(golem.state, "constitution"), "normal");
  assert.equal(M.effectiveSpeed(golem.state), speedBefore);

  dice([10, 1, 1]);
  const first = BA.resolve(2, 1, golem, setup, "1:clay");
  assert.equal(first.events.length, 1);
  assert.equal(first.events[0].attack_name, "Slam");
  assert.equal(golem.state.bonus_action_available, false);

  golem.state.bonus_action_available = true;
  dice([4, 10, 1, 1]);
  const rechargeFail = R.resolveStartOfTurn(first.sequence, 2, golem);
  assert.equal(rechargeFail.events[0].recharge_succeeded, false);
  assert.equal(golem.state.resources.haste, 0);
  assert.ok(golem.state.active_effect_ids.includes("haste"));
  const second = BA.resolve(rechargeFail.sequence, 2, golem, setup, "2:clay");
  assert.equal(second.events.length, 1);

  const ended = L.resolveSourceTiming(second.sequence, 2, golem, setup, "source_turn_end");
  assert.ok(ended.events.some((item) => item.feature_id === "haste"));
  assert.ok(!golem.state.active_effect_ids.includes("haste"));
  assert.equal(M.effectiveArmorClass(golem.state), 14);
  assert.equal(V.saveMode(golem.state, "dexterity"), "normal");

  golem.state.bonus_action_available = true;
  assert.deepEqual(BA.resolve(ended.sequence, 2, golem, setup, "2:clay").events, []);
  dice([5]);
  const rechargePass = R.resolveStartOfTurn(ended.sequence, 3, golem);
  assert.equal(rechargePass.events[0].recharge_succeeded, true);
  assert.equal(golem.state.resources.haste, 1);
}

console.log("Browser Clay Golem Haste composition parity passed.");
