"use strict";

const { assert, attack, member } = require("./browser-on-hit-condition-test-support.cjs");

try {
  const fighter = member("renamed-escalator", "heroes", {
    onHitConditionSave: {
      saveAbility: "constitution", dc: 12, conditionId: "poisoned",
      durationRounds: 10,
      failureMarginEscalation: {
        margin: 5, additionalConditionIds: ["unconscious"],
        replacementDurationDiceCount: 1, replacementDurationDiceSize: 10,
        replacementDurationRoundMultiplier: 10, endsOnDamage: true,
        allowedRemovalActionIds: ["wake-sleeper"],
      },
    },
  });
  fighter.state.template.attacks[0].name = "Renamed Homebrew Sleep Sting";
  const target = member("escalated-target", "monsters", { position: 5 });
  const event = attack(fighter, target, [15, 4, 4, 3, 4]);

  assert.equal(event.save_succeeded, false);
  assert.equal(
    ["poisoned", "unconscious"].every((id) => event.applied_condition_ids.includes(id)),
    true,
  );
  const poisoned = target.state.timed_effects.find((item) => item.effect_id === "poisoned");
  const sleeping = target.state.timed_effects.find((item) => item.effect_id === "unconscious");
  assert.equal(poisoned.expires_round, 41);
  assert.equal(sleeping.expires_round, 41);
  assert.notEqual(poisoned.source_effect_id, sleeping.source_effect_id);
  assert.equal(sleeping.ends_on_damage, true);
  assert.deepEqual(sleeping.allowed_removal_action_ids, ["wake-sleeper"]);
  assert.equal(target.state.active_effect_ids.includes("prone"), true);
  assert.deepEqual(
    window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS.endDamageSensitive(target.state),
    ["unconscious"],
  );
  assert.equal(target.state.active_effect_ids.includes("poisoned"), true);
  assert.equal(target.state.active_effect_ids.includes("unconscious"), false);
} catch (error) {
  console.error("Failed-save escalation browser regression failed", { error });
  throw error;
}

try {
  const effect = {
    saveAbility: "constitution", dc: 12, conditionId: "poisoned", durationRounds: 10,
    failureMarginEscalation: {
      margin: 5, additionalConditionIds: ["unconscious"],
      replacementDurationDiceCount: 1, replacementDurationDiceSize: 10,
      replacementDurationRoundMultiplier: 10, endsOnDamage: true,
      allowedRemovalActionIds: ["wake-sleeper"],
    },
  };
  for (const [save, expectedSuccess] of [[9, false], [15, true]]) {
    const fighter = member("partial-" + save, "heroes", { onHitConditionSave: effect });
    const target = member("target-" + save, "monsters", { position: 5 });
    const event = attack(fighter, target, [15, 4, 4, save]);
    assert.equal(event.save_succeeded, expectedSuccess);
    assert.equal(target.state.active_effect_ids.includes("unconscious"), false);
  }
} catch (error) {
  console.error("Partial failed-save escalation browser regression failed", { error });
  throw error;
}

try {
  const fighter = member("linked-poison-source", "heroes", {
    onHitConditionSave: {
      saveAbility: "constitution", dc: 10, conditionId: "poisoned", durationRounds: 10,
      failureMarginEscalation: {
        margin: 5, additionalConditionIds: ["unconscious"],
        replacementDurationDiceCount: 1, replacementDurationDiceSize: 10,
        replacementDurationRoundMultiplier: 10, endsOnDamage: false,
        allowedRemovalActionIds: [],
      },
    },
  });
  const target = member("linked-sleeper", "monsters", { position: 5 });
  const event = attack(fighter, target, [15, 4, 4, 3, 2]);
  assert.ok(event.applied_condition_ids.includes("unconscious"));
  const poison = target.state.timed_effects.find((item) => item.effect_id === "poisoned");
  const sleep = target.state.timed_effects.find((item) => item.effect_id === "unconscious");
  assert.equal(poison.source_effect_id, sleep.source_effect_id);
  const removed = window.IRON_PIT_BROWSER_TIMED.removeGroup(target.state, poison);
  assert.deepEqual(new Set(removed), new Set(["poisoned", "unconscious"]));
} catch (error) {
  console.error("Grouped failed-save escalation browser regression failed", { error });
  throw error;
}

console.log("Browser failed-save escalation and grouped removal regressions passed.");
