(() => {
  "use strict";

  function apply(state) {
    try {
      for (const grant of state.template.save_success_overrides || []) {
        const remaining = state.resources?.[grant.resource_id] || 0;
        const cost = grant.resource_cost || 1;
        if (remaining < cost) continue;
        state.resources[grant.resource_id] = remaining - cost;
        return grant.source_id;
      }
      return null;
    } catch (error) {
      console.error("Save-success override failed.", { combatant: state?.template?.name, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SAVE_SUCCESS_OVERRIDE = { apply };
})();
