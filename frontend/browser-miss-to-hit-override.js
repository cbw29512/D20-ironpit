(() => {
  "use strict";

  function consumeGrant(state, grant) {
    try {
      if (grant.usage_policy === "resource") {
        const resourceId = grant.resource_id;
        if (!resourceId) throw new Error(`Resource-backed miss-to-hit override ${grant.source_id} has no resource_id.`);
        const remaining = state.resources?.[resourceId];
        if (remaining == null) throw new Error(`Miss-to-hit override ${grant.source_id} references missing resource ${resourceId}.`);
        if (remaining <= 0) return false;
        state.resources[resourceId] -= 1;
        return true;
      }
      if (grant.usage_policy === "refresh_at_turn_start") {
        state.turn_start_feature_cooldowns ||= [];
        if (state.turn_start_feature_cooldowns.includes(grant.source_id)) return false;
        state.turn_start_feature_cooldowns.push(grant.source_id);
        return true;
      }
      throw new Error(`Unsupported miss-to-hit usage policy: ${grant.usage_policy}.`);
    } catch (error) {
      console.error("Failed browser miss-to-hit usage consumption", { error, combatant: state?.template?.name });
      throw error;
    }
  }

  function apply(state, hit) {
    try {
      if (hit) return { hit: true, featureId: null, sourceName: null };

      for (const grant of state.template?.miss_to_hit_override_grants || []) {
        if (consumeGrant(state, grant)) {
          return { hit: true, featureId: grant.source_id, sourceName: grant.source_name };
        }
      }

      // Transitional compatibility for already-certified source data.
      const resourceId = state.template?.miss_to_hit_override_resource_id || null;
      if (!resourceId) return { hit: false, featureId: null, sourceName: null };
      const remaining = state.resources?.[resourceId];
      if (remaining == null) throw new Error(`Miss-to-hit override references missing resource ${resourceId}.`);
      if (remaining <= 0) return { hit: false, featureId: null, sourceName: null };

      state.resources[resourceId] -= 1;
      return {
        hit: true,
        featureId: resourceId,
        sourceName: state.template?.miss_to_hit_override_source_name || resourceId,
      };
    } catch (error) {
      console.error("Failed browser miss-to-hit override", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_MISS_TO_HIT_OVERRIDE = { apply };
})();
