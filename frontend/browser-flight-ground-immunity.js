(() => {
  "use strict";

  function isFlying(state) {
    try {
      const modes = window.IRON_PIT_BROWSER_STATE?.effectiveMovementModes?.(state)
        || state?.template?.movement_modes
        || {};
      return Number(modes.fly_ft || 0) > 0;
    } catch (error) {
      console.error("Failed browser flying check", { combatant: state?.template?.name, error });
      throw error;
    }
  }

  function countersGroundContact(state, groundContact) {
    try {
      return Boolean(groundContact) && isFlying(state);
    } catch (error) {
      console.error("Failed browser ground-contact flying counter", {
        combatant: state?.template?.name, error,
      });
      throw error;
    }
  }

  function resolveGroundConditions(state) {
    try {
      if (!isFlying(state)) return [];
      const timed = window.IRON_PIT_BROWSER_TIMED;
      if (!timed) return [];
      const resolved = [];
      for (const effect of [...(state.timed_effects || [])]) {
        if (!effect.ground_contact) continue;
        const removed = timed.removeGroup(state, effect);
        for (const conditionId of removed) {
          resolved.push({ debuffId: conditionId, sourceId: effect.source_id, movementCost: 0 });
        }
      }
      return resolved;
    } catch (error) {
      console.error("Failed browser flyer ground-debuff clear", {
        combatant: state?.template?.name, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_FLIGHT_GROUND = { countersGroundContact, isFlying, resolveGroundConditions };
})();
