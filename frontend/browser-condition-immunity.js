(() => {
  "use strict";

  function immune(state, conditionId, sourceTemplate = null, options = {}) {
    try {
      if (state.template.condition_immunities?.includes(conditionId) === true) return true;
      if (options.sourceIsMagical === true && (state.timed_effects || []).some((effect) =>
        (effect.owned_magical_condition_immunities || []).includes(conditionId))) return true;
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
