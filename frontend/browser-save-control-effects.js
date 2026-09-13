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
    const effectId = control?.conditionId || control?.effectId;
    if (!effectId || !target.state.is_alive || target.state.is_dead) return [];
    const expiresRound = control.durationRounds != null ? round + control.durationRounds : null;
    const applied = T().apply(target.state, effectId, actor.combatant_id, {
      sourceEffectId: action.id,
      appliedRound: round,
      expiresRound,
      expiresAtStartOfSourceTurn: Boolean(control.expiresAtStartOfSourceTurn),
      expiryTiming: control.expiryTiming || null,
      repeatSaveAbility: control.repeatSaveAbility || null,
      repeatSaveDc: control.repeatSaveDc ?? null,
      repeatSaveTiming: control.repeatSaveTiming || null,
      allowedRemovalActionIds: control.allowedRemovalActionIds || [],
      endsOnDamage: Boolean(control.endsOnDamage),
      sourceEffectImmunityOnEnd: Boolean(control.sourceEffectImmunityOnEnd),
      speedMultiplier: control.speedMultiplier ?? 1,
      blocksReactions: Boolean(control.blocksReactions),
      actionBonusExclusive: Boolean(control.actionBonusExclusive),
      maxAttacksPerTurn: control.maxAttacksPerTurn ?? null,
      disadvantageStrengthD20Tests: Boolean(control.disadvantageStrengthD20Tests),
    });
    return applied ? [applied] : [];
  }

  window.IRON_PIT_BROWSER_SAVE_CONTROL = { applyOutcome, targetImmune };
})();