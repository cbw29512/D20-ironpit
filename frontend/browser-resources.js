(() => {
  "use strict";

  const resolvedId = (resourceId, fallbackResourceId = null) => resourceId || fallbackResourceId || null;

  function current(state, resourceId) {
    try {
      if (!resourceId) return null;
      const value = state.resources?.[resourceId];
      if (!Number.isInteger(value) || value < 0) {
        throw new Error(`Missing or invalid runtime resource ${resourceId}.`);
      }
      return value;
    } catch (error) {
      console.error("Failed browser resource lookup", { resourceId, combatant: state.template?.id, error });
      throw error;
    }
  }

  function available(state, resourceId, cost = 1) {
    try {
      if (!resourceId) return true;
      if (!Number.isInteger(cost) || cost < 1) throw new Error("Resource cost must be a positive integer.");
      return current(state, resourceId) >= cost;
    } catch (error) {
      console.error("Failed browser resource availability check", { resourceId, cost, error });
      throw error;
    }
  }

  function actionAvailable(state, resourceId, cost = 1, fallbackResourceId = null) {
    try {
      if (!Number.isInteger(cost) || cost < 1) throw new Error("Resource cost must be a positive integer.");
      const resolved = resolvedId(resourceId, fallbackResourceId);
      if (!resolved) return true;
      const value = state.resources?.[resolved];
      if (value === undefined) return false;
      if (!Number.isInteger(value) || value < 0) {
        throw new Error(`Invalid runtime resource ${resolved}.`);
      }
      return value >= cost;
    } catch (error) {
      console.error("Failed browser action resource availability check", { resourceId, fallbackResourceId, cost, error });
      throw error;
    }
  }

  function spend(state, resourceId, cost = 1) {
    try {
      if (!resourceId) return null;
      if (!available(state, resourceId, cost)) {
        throw new Error(`Resource ${resourceId} does not have ${cost} use(s) available.`);
      }
      state.resources[resourceId] -= cost;
      return state.resources[resourceId];
    } catch (error) {
      console.error("Failed browser resource spend", { resourceId, cost, error });
      throw error;
    }
  }

  function spendAction(state, resourceId, cost = 1, fallbackResourceId = null) {
    return spend(state, resolvedId(resourceId, fallbackResourceId), cost);
  }

  window.IRON_PIT_BROWSER_RESOURCES = {
    actionAvailable, available, current, resolvedId, spend, spendAction,
  };
})();
