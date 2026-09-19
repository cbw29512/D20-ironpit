(() => {
  "use strict";

  function unlimited(state, resourceId) {
    return (state.template.unlimited_resources || []).includes(resourceId);
  }

  function available(state, resourceId, cost = 1) {
    try {
      if (!resourceId) return true;
      if (unlimited(state, resourceId)) return true;
      return (state.resources[resourceId] || 0) >= cost;
    } catch (error) {
      console.error("Browser resource availability failed", { resourceId, combatant: state?.template?.name, error });
      throw error;
    }
  }

  function spend(state, resourceId, cost = 1) {
    try {
      if (!resourceId || unlimited(state, resourceId)) return null;
      if (!available(state, resourceId, cost)) throw new Error(`Resource ${resourceId} is unavailable.`);
      state.resources[resourceId] -= cost;
      return state.resources[resourceId];
    } catch (error) {
      console.error("Browser resource spending failed", { resourceId, combatant: state?.template?.name, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_RESOURCES = { available, spend, unlimited };
})();
