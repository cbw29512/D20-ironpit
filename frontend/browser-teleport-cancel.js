(() => {
  "use strict";

  function cancelableIds(state) {
    try {
      const ids = [];
      for (const effect of state.timed_effects || []) {
        if (effect.ends_on_teleport || effect.ground_contact) ids.push(effect.effect_id);
      }
      if ((state.grapple_sources || []).length) {
        ids.push("grappled");
        if (state.grapple_sources.some((source) => source.restrains)) ids.push("restrained");
      }
      return [...new Set(ids)];
    } catch (error) {
      console.error("Failed browser teleport-cancel inventory", {
        combatant: state?.template?.name, error,
      });
      throw error;
    }
  }

  function clear(combatant) {
    try {
      const timed = window.IRON_PIT_BROWSER_TIMED;
      const removed = [];
      for (const effect of [...(combatant.state.timed_effects || [])]) {
        if (!(effect.ends_on_teleport || effect.ground_contact)) continue;
        for (const conditionId of (timed?.removeGroup(combatant.state, effect) || [])) {
          if (!removed.includes(conditionId)) removed.push(conditionId);
        }
      }
      for (const source of [...(combatant.state.grapple_sources || [])]) {
        window.IRON_PIT_BROWSER_GRAPPLE?.release?.(combatant.state, source.source_id);
        if (!removed.includes("grappled")) removed.push("grappled");
        if (source.restrains && !removed.includes("restrained")) removed.push("restrained");
      }
      return removed;
    } catch (error) {
      console.error("Failed browser in-place teleport cancel", {
        combatant: combatant?.combatant_id, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_TELEPORT_CANCEL = { cancelableIds, clear };
})();
