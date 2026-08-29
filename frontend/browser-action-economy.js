(() => {
  "use strict";

  const INCAPACITATED = new Set(["incapacitated", "paralyzed", "stunned"]);

  function isIncapacitated(state) {
    return Boolean(state.is_dead || state.is_unconscious || state.active_effect_ids?.some((id) => INCAPACITATED.has(id)));
  }

  function available(state, cost) {
    if (isIncapacitated(state)) return false;
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

  window.IRON_PIT_ACTION_ECONOMY = { available, isIncapacitated, spend };
})();
