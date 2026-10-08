(() => {
  "use strict";

  const C = () => window.IRON_PIT_BROWSER_DEBUFF_COUNTERS || { prevented: () => false };

  function immune(state, conditionId, sourceTemplate = null, options = {}) {
    try {
      if (state.template.condition_immunities?.includes(conditionId) === true) return true;
      if (window.IRON_PIT_BROWSER_FLIGHT_GROUND?.countersGroundContact(state, options.groundContact === true)) {
        return true;
      }
      if (C().prevented(state, conditionId, { sourceIsMagical: options.sourceIsMagical === true })) return true;
      const hasAlly = options.activeAllyPresent === true || (options.member && options.setup
        && window.IRON_PIT_BROWSER_STATE?.hasActiveAlly(options.member, options.setup) === true);
      if (window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS?.conditionImmune(state, conditionId, sourceTemplate,
        { ...options, activeAllyPresent: hasAlly })) return true;
      if (state.template.ruleset !== "2014" && state.template.mindless_rage
          && state.active_effect_ids.includes("rage")
          && ["charmed", "frightened"].includes(conditionId)) return true;
      if (conditionId === "poisoned") return (state.active_effect_ids || []).includes("petrified");
      return false;
    } catch (error) {
      console.error("Condition immunity lookup failed.", error);
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune };
})();
