(() => {
  "use strict";
  const D = () => window.IRON_PIT_DICE;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };

  function escalation(effect, save) {
    const spec = effect.failureMarginEscalation;
    if (!spec || save.succeeded || !save.roll || effect.dc - save.roll.total < spec.margin) {
      return { conditionIds: [], durationRounds: effect.durationRounds ?? null, spec: null };
    }
    let durationRounds = effect.durationRounds ?? null;
    if (spec.replacementDurationRounds != null) durationRounds = spec.replacementDurationRounds;
    else if (spec.replacementDurationDiceCount) {
      const rolls = D().rollMany(spec.replacementDurationDiceCount, spec.replacementDurationDiceSize);
      durationRounds = rolls.reduce((sum, roll) => sum + roll, 0) * (spec.replacementDurationRoundMultiplier || 1);
    }
    return { conditionIds: [...(spec.additionalConditionIds || [])], durationRounds, spec };
  }

  function applyOne(target, attack, effect, conditionId, sourceId, round, durationRounds, repeat, lifecycle = {}) {
    if (I().immune(target.state, conditionId)) return null;
    const endsOnDamage = Boolean(lifecycle.endsOnDamage);
    const allowedRemovalActionIds = [...(lifecycle.allowedRemovalActionIds || [])];
    const timed = durationRounds != null || (repeat && effect.repeatSaveTiming) || endsOnDamage || allowedRemovalActionIds.length > 0;
    if (timed) {
      if (!sourceId || round == null || !T()) throw new Error("Timed on-hit save effect lacks browser source context.");
      return T().apply(target.state, conditionId, sourceId, {
        sourceEffectId: attack.id, appliedRound: round,
        expiresRound: durationRounds != null ? round + durationRounds : null,
        repeatSaveAbility: repeat && effect.repeatSaveTiming ? effect.saveAbility : null,
        repeatSaveDc: repeat && effect.repeatSaveTiming ? effect.dc : null,
        repeatSaveTiming: repeat ? effect.repeatSaveTiming || null : null,
        repeatSaveFailureConditionId: repeat ? effect.repeatSaveFailureConditionId || null : null,
        endsOnDamage, allowedRemovalActionIds,
      });
    }
    if (!target.state.active_effect_ids.includes(conditionId)) target.state.active_effect_ids.push(conditionId);
    return conditionId;
  }

  function applyFailure(target, attack, effect, save, sourceId, round) {
    if (!effect.conditionId || save.succeeded || !target.state.is_alive || target.state.is_dead) {
      return { appliedCondition: null, appliedConditions: [] };
    }
    const resolved = escalation(effect, save);
    const primary = applyOne(
      target, attack, effect, effect.conditionId, sourceId, round, resolved.durationRounds, true,
      { endsOnDamage: effect.endsOnDamage },
    );
    if (!primary) return { appliedCondition: null, appliedConditions: [] };
    const applied = [primary];
    for (const conditionId of resolved.conditionIds) {
      const extra = applyOne(
        target, attack, effect, conditionId, sourceId, round, resolved.durationRounds, false,
        resolved.spec || {},
      );
      if (extra) applied.push(extra);
    }
    return { appliedCondition: primary, appliedConditions: [...new Set(applied)] };
  }

  window.IRON_PIT_BROWSER_ON_HIT_SAVE_CONDITIONS = { applyFailure, escalation };
})();
