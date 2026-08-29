(() => {
  "use strict";

  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || {
    incapacitated: (state) => Boolean(state.is_unconscious),
  };

  function available(state, cost) {
    if (state.is_dead || Q().incapacitated(state)) return false;
    if (cost === "action") return Boolean(state.action_available);
    if (cost === "bonus_action") return Boolean(state.bonus_action_available);
    if (cost === "reaction") return Boolean(state.reaction_available);
    throw new Error(`Unknown action cost: ${cost}`);
  }

  function spend(state, cost) {
    if (!available(state, cost)) throw new Error(`${cost} is not available.`);
    if (cost === "action") state.action_available = false;
    else if (cost === "bonus_action") state.bonus_action_available = false;
    else state.reaction_available = false;
  }

  window.IRON_PIT_ACTION_ECONOMY = { available, isIncapacitated: (state) => Q().incapacitated(state), spend };
})();
