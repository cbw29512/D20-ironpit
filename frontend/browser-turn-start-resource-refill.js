(() => {
  "use strict";

  function resolve(state) {
    try {
      for (const resourceId of state.template.turn_start_resource_refill_ids || []) {
        if (!Object.prototype.hasOwnProperty.call(state.resources || {}, resourceId)) {
          throw new Error(`Turn-start refill references missing resource ${resourceId} on ${state.template.name}.`);
        }
        const maximum = state.template.resources?.[resourceId];
        if (!Number.isInteger(maximum)) {
          throw new Error(`Turn-start refill resource ${resourceId} has no certified maximum.`);
        }
        state.resources[resourceId] = maximum;
      }
    } catch (error) {
      console.error("Browser turn-start resource refill failed.", {
        combatant: state?.template?.name,
        error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_TURN_START_RESOURCE_REFILL = { resolve };
})();
