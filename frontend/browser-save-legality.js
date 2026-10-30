(() => {
  "use strict";

  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { has: () => false };
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const T = () => window.IRON_PIT_BROWSER_TIMED;

  function legalAction(action, target, distance, actor = null, setup = null) {
    try {
      if (distance > action.range) return false;
      if (action.requiredTargetCondition && !Q().has(target.state, action.requiredTargetCondition)) return false;
      if (action.requiredTargetGrappledBySelf) {
        if (!actor || !(target.state.grapple_sources || []).some((source) => source.source_id === actor.combatant_id)) return false;
      }
      if (action.maxActiveGrappleTargets != null) {
        if (!actor || !setup) return false;
        const active = [...setup.heroes, ...setup.monsters].filter((member) =>
          (member.state.grapple_sources || []).some((source) =>
            source.source_id === actor.combatant_id && source.source_effect_id === action.id
          )
        );
        const already = active.some((member) => member.combatant_id === target.combatant_id);
        if (!already && active.length >= action.maxActiveGrappleTargets) return false;
      }
      if (action.forbidTargetAffectedByAction && T()?.affectedByAction(target.state, action.id)) return false;
      return !action.targetMaxSize || S().sizeAtMost(target, action.targetMaxSize);
    } catch (error) {
      console.error("Browser save-action legality failed.", { action: action?.id, error });
      throw error;
    }
  }

  function pushAway(actor, target, action) {
    try {
      const distance = action.pushTargetAwayFt || 0;
      if (!distance || !target.state.is_alive || target.state.is_dead) return 0;
      if (action.pushTargetMaxSize && !S().sizeAtMost(target, action.pushTargetMaxSize)) return 0;
      const start = target.position_ft, direction = start >= actor.position_ft ? 1 : -1;
      target.position_ft = Math.max(0, start + direction * distance);
      return Math.abs(target.position_ft - start);
    } catch (error) {
      console.error("Browser failed-save push failed.", { actor: actor?.combatant_id, target: target?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SAVE_LEGALITY = { legalAction, pushAway };
})();
