(() => {
  "use strict";

  function startOfTurn(state) {
    try {
      for (const resourceId of state.template?.start_of_turn_resource_refresh_ids || []) {
        if (state.resources?.[resourceId] == null) {
          throw new Error(`Start-of-turn refresh references missing resource ${resourceId}.`);
        }
        const maximum = state.template.resources?.[resourceId];
        if (maximum == null) {
          throw new Error(`Start-of-turn refresh references missing resource definition ${resourceId}.`);
        }
        state.resources[resourceId] = maximum;
      }
    } catch (error) {
      console.error("Failed browser start-of-turn resource refresh", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_RESOURCE_REFRESH = { startOfTurn };
})();
