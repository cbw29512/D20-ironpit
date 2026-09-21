(() => {
  "use strict";

  function apply(state, hit) {
    try {
      if (hit) return { hit: true, featureId: null };
      const resourceId = state.template?.miss_to_hit_override_resource_id || null;
      if (!resourceId) return { hit: false, featureId: null };
      const remaining = state.resources?.[resourceId];
      if (remaining == null) throw new Error(`Miss-to-hit override references missing resource ${resourceId}.`);
      if (remaining <= 0) return { hit: false, featureId: null };
      state.resources[resourceId] -= 1;
      return { hit: true, featureId: resourceId };
    } catch (error) {
      console.error("Failed browser miss-to-hit override", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_MISS_TO_HIT_OVERRIDE = { apply };
})();
