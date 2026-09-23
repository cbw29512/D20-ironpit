(() => {
  "use strict";

  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES;

  function has(state, conditionId) {
    try {
      if (Q()?.has) return Q().has(state, conditionId);
      return Boolean(state?.active_effect_ids?.includes(conditionId));
    } catch (error) {
      console.error("Failed browser visibility condition lookup.", { conditionId, error });
      throw error;
    }
  }

  function canSee(observer, target, distanceFt) {
    try {
      if (!Number.isFinite(distanceFt) || distanceFt < 0) {
        throw new Error("Visibility distance must be a non-negative number.");
      }
      const senses = observer?.state?.template?.senses || observer?.template?.senses || {};
      const observerState = observer?.state || observer;
      const targetState = target?.state || target;
      const blindsight = Number(senses.blindsight_ft || 0);
      const hearingBlocked = Boolean(
        senses.blindsight_requires_hearing && has(observerState, "deafened"),
      );
      if (blindsight > 0 && distanceFt <= blindsight && !hearingBlocked) return true;
      if (has(observerState, "blinded")) return false;
      const blindBeyond = senses.blind_beyond_ft;
      if (blindBeyond != null && distanceFt > Number(blindBeyond)) return false;
      if (has(targetState, "invisible")) {
        const truesight = Number(senses.truesight_ft || 0);
        return truesight > 0 && distanceFt <= truesight;
      }
      return true;
    } catch (error) {
      console.error("Failed browser visibility resolution.", {
        observer: observer?.combatant_id || observer?.template?.name,
        target: target?.combatant_id || target?.template?.name,
        error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_VISIBILITY = { canSee };
})();
