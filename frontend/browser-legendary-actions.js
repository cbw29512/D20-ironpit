(() => {
  "use strict";

  function initialize(state) {
    try {
      const pool = state.template.legendary_actions;
      state.legendary_action_uses_remaining = pool ? pool.max_uses : 0;
      state.legendary_action_locked_option_ids = [];
    } catch (error) {
      console.error("Failed browser legendary-action initialization", { error });
      throw error;
    }
  }

  function refresh(state) {
    initialize(state);
  }

  function option(state, optionId) {
    return state.template.legendary_actions?.options?.find((item) => item.id === optionId) || null;
  }

  function incapacitated(state) {
    const rules = window.IRON_PIT_BROWSER_CONDITION_RULES;
    return rules ? rules.incapacitated(state) : Boolean(state.is_unconscious || state.active_effect_ids?.includes("incapacitated"));
  }

  function canSpend(state, optionId, ownerId, completedTurnId) {
    try {
      const choice = option(state, optionId);
      if (!choice || ownerId === completedTurnId) return false;
      if (state.is_dead || incapacitated(state)) return false;
      if ((state.legendary_action_locked_option_ids || []).includes(optionId)) return false;
      return (state.legendary_action_uses_remaining || 0) >= choice.cost;
    } catch (error) {
      console.error("Failed browser legendary-action legality check", { optionId, error });
      throw error;
    }
  }

  function spend(state, optionId) {
    try {
      const choice = option(state, optionId);
      if (!choice) throw new Error(`Unknown legendary action option: ${optionId}`);
      if ((state.legendary_action_uses_remaining || 0) < choice.cost) {
        throw new Error("Insufficient legendary action uses.");
      }
      state.legendary_action_uses_remaining -= choice.cost;
      if (choice.once_until_owner_turn) state.legendary_action_locked_option_ids.push(choice.id);
    } catch (error) {
      console.error("Failed browser legendary-action spend", { optionId, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_LEGENDARY_ACTIONS = { canSpend, initialize, refresh, spend };
})();