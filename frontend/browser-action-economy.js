(() => {
  "use strict";

  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || {
    incapacitated: (state) => Boolean(state.is_unconscious),
  };
  const T = () => window.IRON_PIT_BROWSER_TIMED || {
    suppressesAction: () => false,
    suppressesBonusAction: () => false,
    suppressesReactions: () => false,
  };

  const singleActivityRestricted = (state) => (state.timed_effects || []).some((effect) => effect.turn_behavior === "single_activity");
  const actionBonusExclusive = (state) => Boolean(window.IRON_PIT_BROWSER_TIMED_CONTROL?.actionBonusExclusive(state));
  function voluntaryActivityAvailable(state, activity) {
    if (singleActivityRestricted(state)) {
      return state.voluntary_turn_activity == null || state.voluntary_turn_activity === activity;
    }
    if (actionBonusExclusive(state) && (activity === "action" || activity === "bonus_action")) {
      return state.voluntary_turn_activity == null || state.voluntary_turn_activity === activity;
    }
    return true;
  }
  function claimActivity(state, activity) {
    if (singleActivityRestricted(state)) {
      if (!voluntaryActivityAvailable(state, activity)) throw new Error("A different voluntary turn activity is already committed.");
      state.voluntary_turn_activity = activity;
      if (activity === "movement") { state.action_available = false; state.bonus_action_available = false; }
      else if (activity === "action") { state.bonus_action_available = false; state.movement_remaining_ft = 0; }
      else { state.action_available = false; state.movement_remaining_ft = 0; }
      return;
    }
    if (actionBonusExclusive(state) && (activity === "action" || activity === "bonus_action")) {
      if (!voluntaryActivityAvailable(state, activity)) throw new Error("Action and Bonus Action cannot both be used under this effect.");
      state.voluntary_turn_activity = activity;
      if (activity === "action") state.bonus_action_available = false;
      else state.action_available = false;
    }
  }

  const committedActivity = (state) => Boolean((state.delayed_resource_refills || []).length);
  function available(state, cost) {
    if (state.is_dead || Q().incapacitated(state)) return false;
    if (state.turn_terminated && cost !== "reaction") return false;
    if (cost === "action") return Boolean(state.action_available) && !committedActivity(state) && !T().suppressesAction(state) && voluntaryActivityAvailable(state, "action");
    if (cost === "bonus_action") return Boolean(state.bonus_action_available) && !committedActivity(state) && !T().suppressesBonusAction(state) && voluntaryActivityAvailable(state, "bonus_action");
    if (cost === "reaction") return Boolean(state.reaction_available) && !T().suppressesReactions(state);
    throw new Error(`Unknown action cost: ${cost}`);
  }

  function spend(state, cost) {
    if (!available(state, cost)) throw new Error(`${cost} is not available.`);
    if (cost === "action") { claimActivity(state, "action"); state.action_available = false; }
    else if (cost === "bonus_action") { claimActivity(state, "bonus_action"); state.bonus_action_available = false; }
    else state.reaction_available = false;
  }

  window.IRON_PIT_ACTION_ECONOMY = { available, claimActivity, isIncapacitated: (state) => Q().incapacitated(state), singleActivityRestricted, spend, voluntaryActivityAvailable };
})();