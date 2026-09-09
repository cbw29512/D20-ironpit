(() => {
  "use strict";

  const G = () => window.IRON_PIT_BROWSER_GRAPPLE;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const T = () => window.IRON_PIT_BROWSER_TIMED;

  function apply(target, effects, sourceId, sourceEffectId, range, round) {
    if (!target?.state?.is_alive || target.state.is_dead) return [];
    const applied = [];
    for (const effect of effects || []) {
      if (effect.maxTargetSize && !S().sizeAtMost(target, effect.maxTargetSize)) continue;
      if (effect.grappleEscapeDc) {
        applied.push(...G().apply(
          target.state,
          sourceId,
          effect.grappleEscapeDc,
          range,
          Boolean(effect.restrainsWhileGrappled),
        ));
      }
      if (!effect.conditionId) continue;
      const condition = T().apply(target.state, effect.conditionId, sourceId, {
        sourceEffectId,
        appliedRound: round,
        expiresAtStartOfSourceTurn: Boolean(effect.expiresAtStartOfSourceTurn),
        expiryTiming: effect.expiryTiming || null,
        repeatSaveAbility: effect.repeatSaveAbility || null,
        repeatSaveDc: effect.repeatSaveDc || null,
        repeatSaveTiming: effect.repeatSaveTiming || null,
        allowedRemovalActionIds: effect.allowedRemovalActionIds || [],
      });
      if (condition) applied.push(condition);
    }
    return [...new Set(applied)];
  }

  window.IRON_PIT_BROWSER_PERSISTENT_EFFECTS = { apply };
})();
