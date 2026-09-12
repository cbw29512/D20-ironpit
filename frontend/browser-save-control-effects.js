(() => {
  "use strict";

  const I = () => window.IRON_PIT_BROWSER_SOURCE_EFFECT_IMMUNITY;
  const T = () => window.IRON_PIT_BROWSER_TIMED;

  function targetImmune(actor, target, action) {
    return I().immune(target.state, actor.combatant_id, action.id);
  }

  function applyOutcome(actor, target, action, succeeded, round) {
    if (succeeded) {
      if (action.sourceEffectImmunityOnSuccess) I().grant(target.state, actor.combatant_id, action.id);
      return [];
    }
    const control = action.failureControlEffect;
    if (!control?.conditionId || !target.state.is_alive || target.state.is_dead) return [];
    const expiresRound = control.durationRounds != null ? round + control.durationRounds : null;
    const applied = T().apply(target.state, control.conditionId, actor.combatant_id, {
      sourceEffectId: action.id,
      appliedRound: round,
      expiresRound,
      expiresAtStartOfSourceTurn: Boolean(control.expiresAtStartOfSourceTurn),
      expiryTiming: control.expiryTiming || null,
      repeatSaveAbility: control.repeatSaveAbility || null,
      repeatSaveDc: control.repeatSaveDc ?? null,
      repeatSaveTiming: control.repeatSaveTiming || null,
      allowedRemovalActionIds: control.allowedRemovalActionIds || [],
      sourceEffectImmunityOnEnd: Boolean(control.sourceEffectImmunityOnEnd),
    });
    return applied ? [applied] : [];
  }

  window.IRON_PIT_BROWSER_SAVE_CONTROL = { applyOutcome, targetImmune };
})();
