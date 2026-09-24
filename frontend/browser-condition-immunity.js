(() => {
  "use strict";

  const C = () => window.IRON_PIT_BROWSER_DEBUFF_COUNTERS || { prevented: () => false };

  function immune(state, conditionId, sourceTemplate = null, options = {}) {
    try {
      if (state.template.condition_immunities?.includes(conditionId) === true) return true;
      if (C().prevented(state, conditionId, { sourceIsMagical: options.sourceIsMagical === true })) return true;
      if (window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS?.conditionImmune(state, conditionId, sourceTemplate)) return true;
      if (state.template.mindless_rage && state.active_effect_ids.includes("rage")
          && ["charmed", "frightened"].includes(conditionId)) return true;
      if (conditionId === "poisoned") {
        const active = [...(state.active_effect_ids || []), ...(state.active_buff_effect_ids || [])];
        return active.includes("petrified") || active.includes("protection-from-poison");
      }
      return false;
    } catch (error) {
      console.error("Condition immunity lookup failed.", error);
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune };
})();
